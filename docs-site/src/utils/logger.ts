const noop = (..._args: unknown[]): void => undefined;

const logger = {
    debug: noop,
    info: noop,
    log: noop,
    warn: noop,
    error: noop,
    group: noop,
    groupCollapsed: noop,
    groupEnd: (): void => undefined,
};

export default logger;
