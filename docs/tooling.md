<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="../README.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Project Overview</a>
</div>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🛠️</span> Tooling & Libraries Applied to Generative AI Implementation Lifecycle for Shieldcraft
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
Key tools and libraries, and how they apply to the various steps in the Generative AI implementation lifecycle for Shieldcraft.
</div>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h3 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.2em;">📋</span>Tools & Libraries
</h3>
<ul style="margin-bottom:0.5em;">
  <li><b>Machine Learning/Deep Learning Frameworks:</b> PyTorch, TensorFlow, Scikit-learn, XGBoost / LightGBM</li>
  <li><b>Data Processing & Engineering:</b> Apache Spark (via AWS Glue/EMR), Pandas, NumPy, Kafka / AWS Kinesis</li>
  <li><b>Graph Databases & Analytics:</b> Amazon Neptune</li>
  <li><b>MLOps Platforms & Tools:</b> AWS SageMaker (Studio, Experiments, Model Registry, Model Monitor, Feature Store), MLflow</li>
  <li><b>Observability & Monitoring:</b> Prometheus, Grafana, AWS X-Ray, AWS CloudWatch</li>
  <li><b>Infrastructure as Code & Orchestration:</b> AWS CDK, Docker, Kubernetes (AWS EKS)</li>
  <li><b>Generative AI Orchestration:</b> LangChain</li>
  <li><b>Foundation Models (FMs):</b> Amazon Bedrock (Anthropic Claude, Amazon Titan, AI21 Labs Jurassic)</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h3 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.2em;">🔗</span> Application to Generative AI Implementation Lifecycle Steps
</h3>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">🔍</span> 1. Discovery & Use Case Definition
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b>Primarily strategic and documentation tools like Confluence, Jira, etc. for planning.</li>
  <li><b>Application:</b> This phase is about defining <em>what</em> to build. The choice of specific FMs from <b>Amazon Bedrock</b> will be based on the identified use cases (e.g., Claude for complex summarization, Titan for text embeddings).</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">📥</span> 2. Data Preparation & Retrieval Strategy
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b> <b>Apache Spark (AWS Glue/EMR)</b>, <b>Pandas</b>, <b>NumPy</b>, <b>Kafka / AWS Kinesis</b>, <b>Amazon Neptune</b>, <b>AWS SageMaker Feature Store</b>.</li>
  <li><b>Application:</b>
    <ul>
      <li><b>Kafka / AWS Kinesis:</b> For real-time ingestion of security logs and threat intelligence.</li>
      <li><b>Apache Spark (AWS Glue/EMR):</b> For large-scale data cleaning, preprocessing, and text chunking for RAG.</li>
      <li><b>Pandas / NumPy:</b> For smaller-scale data manipulation and feature engineering during development.</li>
      <li><b>Amazon Neptune:</b> To model and extract relationships from security data (e.g., entity graphs) that can enrich RAG context.</li>
      <li><b>AWS SageMaker Feature Store:</b> To manage and serve processed features and embeddings consistently.</li>
      <li><b>Amazon Bedrock (Embedding Models):</b> Used to generate embeddings from security data for the vector database.</li>
    </ul>
  </li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">🧠</span> 3. Model Selection, Prompt Engineering & Initial Prototyping
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b> <b>Amazon Bedrock</b>, <b>LangChain</b>.</li>
  <li><b>Application:</b>
    <ul>
      <li><b>Amazon Bedrock:</b> Accessing various Foundation Models (FMs) for initial experimentation and selection based on task performance.</li>
      <li><b>LangChain:</b> Directly used here to:
        <ul>
          <li>Simplify interaction with <b>Amazon Bedrock</b> FMs.</li>
          <li>Begin building basic RAG pipelines by connecting FMs with the prepared vector data.</li>
          <li>Experiment with prompt templates and chains.</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">🔗</span> 4. Application Integration & Orchestration
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b> <b>LangChain</b>, <b>Docker</b>, <b>Kubernetes (AWS EKS)</b>.</li>
  <li><b>Application:</b>
    <ul>
      <li><b>LangChain:</b> Develop robust <code>Chains</code> and <code>Agents</code> to orchestrate multi-step Generative AI workflows, enable tool use (e.g., querying databases, interacting with SOAR via API calls), and manage conversational <code>Memory</code>.</li>
      <li><b>Docker:</b> Containerize the API services and LangChain orchestration layers for consistent deployment.</li>
      <li><b>Kubernetes (AWS EKS):</b> Orchestrate the deployment and scaling of these containerized services.</li>
    </ul>
  </li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">🧪</span> 5. Evaluation, Testing & Refinement
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b> <b>AWS SageMaker Experiments</b>, <b>MLflow</b>, <b>PyTorch / TensorFlow</b>, <b>Scikit-learn / XGBoost / LightGBM</b>, <b>Prometheus</b>, <b>Grafana</b>, <b>AWS CloudWatch</b>.</li>
  <li><b>Application:</b>
    <ul>
      <li><b>AWS SageMaker Experiments / MLflow:</b> Track different prompt versions, RAG configurations, and evaluation metrics (both automated and human feedback).</li>
      <li><b>PyTorch / TensorFlow / Scikit-learn / XGBoost / LightGBM:</b> Used to potentially train auxiliary models for automated evaluation or to re-evaluate the performance of existing behavioral models that feed into the GenAI context.</li>
      <li><b>Prometheus / Grafana / AWS CloudWatch:</b> Monitor API performance, latency of GenAI responses, and LLM token usage during testing.</li>
    </ul>
  </li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h4 style="margin-top:0;display:flex;align-items:center;font-size:1.15em;gap:0.5em;">
  <span style="font-size:1.2em;">🚀</span> 6. Deployment, MLOps & Monitoring
</h4>
<ul style="margin-bottom:0.5em;">
  <li><b>Tools:</b> <b>AWS CDK</b>, <b>Docker</b>, <b>Kubernetes (AWS EKS)</b>, <b>AWS SageMaker (Model Registry, Model Monitor)</b>, <b>Prometheus</b>, <b>Grafana</b>, <b>AWS X-Ray</b>, <b>AWS CloudWatch</b>.</li>
  <li><b>Application:</b>
    <ul>
      <li><b>AWS CDK:</b> Automate the deployment of all Generative AI infrastructure (LangChain services, vector databases, Bedrock configurations).</li>
      <li><b>Docker & Kubernetes (AWS EKS):</b> For scalable and reliable production deployment of the GenAI application layer.</li>
      <li><b>AWS SageMaker Model Registry:</b> Version and manage the specific FMs used, and potentially custom fine-tuned models if applicable.</li>
      <li><b>AWS SageMaker Model Monitor:</b> Monitor the quality of RAG retrievals, prompt success rates, and potential concept drift in the underlying data affecting GenAI output.</li>
      <li><b>Prometheus / Grafana / AWS CloudWatch:</b> For real-time monitoring of application health, GenAI service metrics, and cost.</li>
      <li><b>AWS X-Ray:</b> For tracing requests through the entire GenAI pipeline (API -> LangChain -> Bedrock -> Vector DB) to identify bottlenecks.</li>
    </ul>
  </li>
</ul>
</section>
