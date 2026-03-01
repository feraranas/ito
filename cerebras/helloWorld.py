# !pip install cerebras-cloud-sdk
import os
from pathlib import Path
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Load environment variables from .env file at project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

completion = client.chat.completions.create(
    messages=[{"role": "user", "content": "Why is fast inference important?"}],
    model="llama-3.3-70b",
    max_completion_tokens=1024,
    temperature=0.2,
    top_p=1,
    stream=False,
)

print(completion.choices[0].message.content)

# Output:

# Fast inference is important for several reasons:

# 1. **Real-time Applications**: Many applications, such as self-driving cars, robotics, and video analysis, require fast and accurate inference to make decisions in real-time. Delayed inference can lead to accidents, errors, or missed opportunities.
# 2. **User Experience**: Fast inference improves the user experience in applications like virtual assistants, chatbots, and image recognition. Quick responses make the interaction feel more natural and engaging.
# 3. **Scalability**: Fast inference enables scalability in large-scale deployments, such as cloud-based services, where thousands of requests are processed simultaneously. Slow inference can lead to bottlenecks, increased latency, and reduced throughput.
# 4. **Energy Efficiency**: Fast inference reduces the energy consumption of devices, which is critical for battery-powered devices like smartphones, smart home devices, and IoT devices. Faster inference means less power consumption, leading to longer battery life.
# 5. **Cost Savings**: Fast inference can lead to cost savings in cloud computing, where customers are charged based on the computational resources used. Faster inference reduces the computational resources required, resulting in lower costs.
# 6. **Competitive Advantage**: In many industries, fast inference can be a competitive advantage. For example, in finance, fast inference can enable quicker trading decisions, while in healthcare, fast inference can lead to faster diagnosis and treatment.
# 7. **Edge Computing**: Fast inference is essential for edge computing, where data is processed at the edge of the network, closer to the source of the data. This reduces latency, improves real-time decision-making, and enhances overall system performance.
# 8. **Model Complexity**: Fast inference allows for the deployment of more complex models, which can lead to improved accuracy and better decision-making. Without fast inference, complex models might be too slow to be practical.
# 9. **Multi-Tasking**: Fast inference enables devices to perform multiple tasks simultaneously, such as voice recognition, image processing, and natural language processing, without significant performance degradation.
# 10. **Emerging Technologies**: Fast inference is crucial for emerging technologies like augmented reality, virtual reality, and autonomous systems, which require rapid processing of large amounts of data to create immersive and interactive experiences.

# In summary, fast inference is essential for many applications, as it enables real-time decision-making, improves user experience, reduces energy consumption, and leads to cost savings, among other benefits.
