"""
StepFunctionsStack for ShieldCraft AI
This stack synthesizes AWS Step Functions state machines from config,
referencing all resources by logical ID/ARN.
"""

from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_iam as iam,
    Duration,
)
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from constructs import Construct
from infra.utils.config_loader import get_config_loader


class StepFunctionsStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, config=None, **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        if config is None:
            config = get_config_loader(env=env_name).get_section("stepfunctions")
        # Defensive: Only synthesize if state_machines is present and non-empty
        if not config or "state_machines" not in config or not config["state_machines"]:
            return  # No state machines defined for this env
        for sm in config["state_machines"]:
            if not sm.get("definition"):
                continue
            definition = self._build_definition(sm["definition"])
            role = iam.Role.from_role_arn(self, f"{sm['id']}Role", sm["role_arn"])
            sfn.StateMachine(
                self,
                sm["id"],
                state_machine_name=sm["name"],
                definition_body=sfn.DefinitionBody.from_chainable(definition),
                role=role,
                state_machine_type=sfn.StateMachineType.STANDARD,
                comment=sm.get("comment"),
            )

    def _build_definition(self, states):
        # Build all state objects first
        from aws_cdk import aws_lambda as _lambda

        state_objs = {}
        for state in states:
            stype = state["type"]
            if stype == "Task":
                lambda_fn = _lambda.Function.from_function_arn(
                    self, f"{state['id']}Task", state["resource"]
                )
                task = sfn_tasks.LambdaInvoke(
                    self,
                    state["id"],
                    lambda_function=lambda_fn,
                    comment=state.get("comment"),
                )
                state_objs[state["id"]] = task
            elif stype == "Choice":
                choice = sfn.Choice(self, state["id"], comment=state.get("comment"))
                state_objs[state["id"]] = choice
            elif stype == "Parallel":
                parallel = sfn.Parallel(self, state["id"], comment=state.get("comment"))
                state_objs[state["id"]] = parallel
            elif stype == "Pass":
                p = sfn.Pass(self, state["id"], comment=state.get("comment"))
                state_objs[state["id"]] = p
            elif stype == "Wait":
                w = sfn.Wait(
                    self,
                    state["id"],
                    time=sfn.WaitTime.duration(
                        Duration.seconds(state.get("seconds", 1))
                    ),
                    comment=state.get("comment"),
                )
                state_objs[state["id"]] = w

        # Wire up transitions and error handling
        for state in states:
            obj = state_objs[state["id"]]
            # Retry
            for retry in state.get("retry", []) or []:
                retry_args = dict(retry)
                # Map interval_seconds to interval=Duration.seconds(...)
                if "interval_seconds" in retry_args:
                    retry_args["interval"] = Duration.seconds(
                        retry_args.pop("interval_seconds")
                    )
                obj.add_retry(**retry_args)
            # Catch
            for catch in state.get("catch", []) or []:
                error_state = state_objs.get(catch["handler"])
                if error_state:
                    obj.add_catch(
                        error_state,
                        **{k: v for k, v in catch.items() if k != "handler"},
                    )
            # Next
            if state.get("next"):
                next_state = state_objs.get(state["next"])
                if next_state:
                    obj.next(next_state)
            # End: no-op, handled by CDK via lack of .next()
            # Choice logic
            if state["type"] == "Choice" and "choices" in state:
                for choice in state["choices"]:
                    cond = getattr(sfn.Condition, choice["condition"])(
                        *choice.get("args", [])
                    )
                    next_state = state_objs.get(choice["next"])
                    if next_state:
                        obj.when(cond, next_state)
                if "default" in state:
                    default_state = state_objs.get(state["default"])
                    if default_state:
                        obj.otherwise(default_state)
            # Parallel logic
            if state["type"] == "Parallel" and "branches" in state:
                for branch in state["branches"]:
                    branch_chain = self._build_definition(branch)
                    obj.branch(branch_chain)
        # Find the entry state (first without any other state pointing to it)
        referenced = set(s.get("next") for s in states if s.get("next"))
        referenced |= set(
            c["next"]
            for s in states
            if s["type"] == "Choice"
            for c in s.get("choices", [])
            if c.get("next")
        )
        referenced |= set(
            b[0]["id"]
            for s in states
            if s["type"] == "Parallel"
            for b in s.get("branches", [])
            if b and b[0].get("id")
        )
        entry = None
        for s in states:
            if s["id"] not in referenced:
                entry = state_objs[s["id"]]
                break
        return entry
