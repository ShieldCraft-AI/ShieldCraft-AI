[⬅️ Back to Project Overview](../../README.md) <!-- BROKEN LINK -->

## 🛠️Tooling & Libraries Applied to Generative AI Implementation Lifecycle for Shieldcraft

Key tools and libraries, and how they apply to the various steps in the Generative AI implementation lifecycle for Shieldcraft.

### 📋Tools & Libraries

* Machine Learning/Deep Learning Frameworks:PyTorch, TensorFlow, Scikit-learn, XGBoost / LightGBM
* Data Processing & Engineering:Apache Spark (via AWS Glue/EMR), Pandas, NumPy, Kafka / AWS Kinesis
* Graph Databases & Analytics:Amazon Neptune
* MLOps Platforms & Tools:AWS SageMaker (Studio, Experiments, Model Registry, Model Monitor, Feature Store), MLflow
* Observability & Monitoring:Prometheus, Grafana, AWS X-Ray, AWS CloudWatch
* Infrastructure as Code & Orchestration:AWS CDK, Docker, Kubernetes (AWS EKS)
* Generative AI Orchestration:LangChain
* Foundation Models (FMs):Amazon Bedrock (Anthropic Claude, Amazon Titan, AI21 Labs Jurassic)

### 🔗Application to Generative AI Implementation Lifecycle Steps

#### 🔍1. Discovery & Use Case Definition

* Tools:Primarily strategic and documentation tools like Confluence, Jira, etc. for planning.
* Application:This phase is about definingwhatto build. The choice of specific FMs fromAmazon Bedrockwill be based on the identified use cases (e.g., Claude for complex summarization, Titan for text embeddings).

#### 📥2. Data Preparation & Retrieval Strategy

* Tools:Apache Spark (AWS Glue/EMR),Pandas,NumPy,Kafka / AWS Kinesis,Amazon Neptune,AWS SageMaker Feature Store.
* Application:Kafka / AWS Kinesis:For real-time ingestion of security logs and threat intelligence.Apache Spark (AWS Glue/EMR):For large-scale data cleaning, preprocessing, and text chunking for RAG.Pandas / NumPy:For smaller-scale data manipulation and feature engineering during development.Amazon Neptune:To model and extract relationships from security data (e.g., entity graphs) that can enrich RAG context.AWS SageMaker Feature Store:To manage and serve processed features and embeddings consistently.Amazon Bedrock (Embedding Models):Used to generate embeddings from security data for the vector database.

#### 🧠3. Model Selection, Prompt Engineering & Initial Prototyping

* Tools:Amazon Bedrock,LangChain.
* Application:Amazon Bedrock:Accessing various Foundation Models (FMs) for initial experimentation and selection based on task performance.LangChain:Directly used here to:Simplify interaction withAmazon BedrockFMs.Begin building basic RAG pipelines by connecting FMs with the prepared vector data.Experiment with prompt templates and chains.

#### 🔗4. Application Integration & Orchestration

* Tools:LangChain,Docker,Kubernetes (AWS EKS).
* Application:LangChain:Develop robustChainsandAgentsto orchestrate multi-step Generative AI workflows, enable tool use (e.g., querying databases, interacting with SOAR via API calls), and manage conversationalMemory.Docker:Containerize the API services and LangChain orchestration layers for consistent deployment.Kubernetes (AWS EKS):Orchestrate the deployment and scaling of these containerized services.

#### 🧪5. Evaluation, Testing & Refinement

* Tools:AWS SageMaker Experiments,MLflow,PyTorch / TensorFlow,Scikit-learn / XGBoost / LightGBM,Prometheus,Grafana,AWS CloudWatch.
* Application:AWS SageMaker Experiments / MLflow:Track different prompt versions, RAG configurations, and evaluation metrics (both automated and human feedback).PyTorch / TensorFlow / Scikit-learn / XGBoost / LightGBM:Used to potentially train auxiliary models for automated evaluation or to re-evaluate the performance of existing behavioral models that feed into the GenAI context.Prometheus / Grafana / AWS CloudWatch:Monitor API performance, latency of GenAI responses, and LLM token usage during testing.

#### 🚀6. Deployment, MLOps & Monitoring

* Tools:AWS CDK,Docker,Kubernetes (AWS EKS),AWS SageMaker (Model Registry, Model Monitor),Prometheus,Grafana,AWS X-Ray,AWS CloudWatch.
* Application:AWS CDK:Automate the deployment of all Generative AI infrastructure (LangChain services, vector databases, Bedrock configurations).Docker & Kubernetes (AWS EKS):For scalable and reliable production deployment of the GenAI application layer.AWS SageMaker Model Registry:Version and manage the specific FMs used, and potentially custom fine-tuned models if applicable.AWS SageMaker Model Monitor:Monitor the quality of RAG retrievals, prompt success rates, and potential concept drift in the underlying data affecting GenAI output.Prometheus / Grafana / AWS CloudWatch:For real-time monitoring of application health, GenAI service metrics, and cost.AWS X-Ray:For tracing requests through the entire GenAI pipeline (API -> LangChain -> Bedrock -> Vector DB) to identify bottlenecks.

<!-- Unhandled tags: li -->

<!-- Broken links detected: ../../README.md -->