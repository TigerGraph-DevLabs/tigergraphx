# Supporting Simple GraphRAG: Part 2 - Context Retrieval and Answer Generation

To run this Jupyter Notebook, you can download the original `.ipynb` file from [simple_graphrag_2.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/simple_graphrag_2.ipynb).

---

## Workflow Overview

The query process of GraphRAG follows this workflow. TigerGraphX serves as the key interface, facilitating interaction with the embedding model to generate embeddings for user queries, retrieving context from TigerGraph, and communicating with the LLM chat model to generate answers.

![](https://github.com/tigergraph/tigergraphx/blob/main/docs/images/graphrag/querying.png?raw=true)

---

## Get the Graph from TigerGraph
Since the graph has already been created in TigerGraph, redefining its schema is unnecessary. Instead, you can provide the graph name to retrieve it. TigerGraphX will verify if the graph exists in TigerGraph and, if it does, will return the corresponding graph.

### Define the TigerGraph Connection Configuration
Before retrive the graph schema from TigerGraph, you shoulddefine the  TigerGraph Connection Configuration first.
The recommended approach is to use environment variables, such as setting them with the `export` command in the shell. Here, to illustrate the demo, we configure them within Python using the `os.environ` method. You can find more methods for configuring connection settings in [Graph.\_\_init\_\_](../reference/01_core/graph.md#tigergraphx.core.graph.Graph.__init__).


```python
>>> import os
>>> os.environ["TG_HOST"] = "http://127.0.0.1"
>>> os.environ["TG_USERNAME"] = "tigergraph"
>>> os.environ["TG_PASSWORD"] = "tigergraph"
```

### Retrieve the Graph
Once a graph has been created in TigerGraph, you can retrieve it without manually defining the schema using the `Graph.from_db` method, which requires only the graph name:


```python
>>> from tigergraphx import Graph
>>> G = Graph.from_db("RetailGraph")
```

---
## Context Building: Writing Custom Context Builders

Context builders play a vital role in graph-powered RAG workflows. They transform retrieved graph data into structured, meaningful contexts for tasks such as interactions with LLMs.

TigerGraphX simplifies this process by offering the flexible `BaseContextBuilder` class, which allows developers to define custom logic for context building. You can find the source code in [this link](https://github.com/TigerGraph-DevLabs/tigergraphx/blob/main/tigergraphx/graphrag/base_context_builder.py).

In this example, we create a simple `ContextBuilder` by implementing the `build_context` method to define how the context is constructed. The process involves:  

- Retrieving the top **k** relevant objects (products) using TigerGraph's vector search.  
- For each retrieved product, fetching its properties and edges.  
- Concatenating all the gathered information into a structured context and returning it.  


```python
>>> from typing import List
>>> from tigergraphx.graphrag import BaseContextBuilder

>>> class ContextBuilder(BaseContextBuilder):
...     async def build_context(self, query: str, k: int = 10) -> str | List[str]:
...         """Build local context."""
...         context: List[str] = []
... 
...         # Retrieve top-k objects
...         top_k_objects: List[str] = await self.retrieve_top_k_objects(
...             query, k=k, oversample_scaler=1
...         )
...         if not top_k_objects:
...             return ""  # Return early if no objects are retrieved
... 
...         # Iterate over all products
...         for product in top_k_objects:
...             node_data = self.graph.get_node_data(product, "Product")
...             edges = self.graph.get_node_edges(product, "Product")
...             context.append(f"Node Data for {product}: {node_data}")
...             context.append(f"Edges for {product}: {edges}")
... 
...         return "\n\n".join(context)
```

    2025-03-28 15:15:41,490 - datasets - INFO - PyTorch version 2.6.0 available.


Here’s how you can utilize the custom context builder to integrate it with TigerGraphX and OpenAI components:  

- **Configure Vector Search:** The `vector_db` settings specify that the search engine will use **TigerVector** to retrieve relevant **Product** nodes based on their `emb_features` attribute.  
- **Set Up OpenAI Components:** The configuration defines models for **LLM**, **embedding**, and **chat**, ensuring that API keys are securely managed via environment variables.  
- **Initialize OpenAI and Search Engine:** The `create_openai_components` function instantiates the OpenAI chat model and the vector-based search engine for retrieving relevant nodes.  
- **Create Context Builder:** The `ContextBuilder` is initialized with the graph and search engine, allowing it to retrieve and structure context dynamically for downstream applications.


```python
>>> from tigergraphx.factories import create_openai_components
>>> settings = {
...     "vector_db": {
...         "type": "TigerVector",
...         "graph_name": "RetailGraph",
...         "node_type": "Product",
...         "vector_attribute_name": "emb_features",
...     },
...     "llm": {
...         "type": "OpenAI",
...         # NOTE: The api_key must be provided via the environment variable OPENAI_API_KEY
...     },
...     "embedding": {
...         "type": "OpenAI",
...         "model": "text-embedding-3-small",
...     },
...     "chat": {
...         "type": "OpenAI",
...         "model": "gpt-4o-mini",
...     },
... }
>>> (openai_chat, search_engine) = create_openai_components(settings, G)
>>> context_builder = ContextBuilder(graph=G, search_engine=search_engine)
```

Let's verify that the context builder functions as expected.


```python
>>> context = await context_builder.build_context("I am looking for a begginer drone. Please give me some recommendations.")
>>> print(context)
```

    2025-03-28 15:15:46,803 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Node Data for SnapShot Voyager Remote Shutter Release: {'name': 'SnapShot Voyager Remote Shutter Release', 'price': 24.99, 'weight': 40, 'features': "Reduced Camera Shake: Allows you to trigger the shutter without touching the camera, minimizing movement and ensuring sharper images. Convenient Control: Provides a comfortable and ergonomic grip with a simple button to activate the shutter. Long Cable: Offers flexibility and ease of use with a generous cable length. Easy Connection: Plugs directly into the camera's remote port for quick and simple setup."}
    
    Edges for SnapShot Voyager Remote Shutter Release: [('SnapShot Voyager Camera 3.0', 'SnapShot Voyager Remote Shutter Release'), ('SnapShot Voyager Remote Shutter Release', 'SnapShot Voyager Camera 3.0'), ('SnapShot Voyager Remote Shutter Release', 'Photography')]
    
    Node Data for Aura X5 Pro: {'name': 'Aura X5 Pro', 'price': 1299, 'weight': 205, 'features': 'Advanced Camera System: Featuring a 50MP primary sensor with OIS, a 12MP ultrawide lens, and a 10MP telephoto lens with 3x optical zoom, the Aura X5 Pro captures professional-quality images in any lighting conditions. Extended Battery Life: The 5000mAh battery delivers all-day power, allowing you to browse, stream, and create without worrying about running out of charge. Supports 65W fast charging. Brilliant Display: Immerse yourself in vibrant colors and sharp details on the 6.7-inch AMOLED display with a 120Hz refresh rate. Powerful Performance: Powered by the Snapdragon 8 Gen 2 processor, the Aura X5 Pro delivers lightning-fast performance for gaming, multitasking, and demanding applications. Enhanced Security: Features an in-display fingerprint sensor and advanced facial recognition for secure and convenient unlocking. Durable Design: Crafted with a premium aluminum frame and Gorilla Glass Victus+ on both the front and back for exceptional durability.'}
    
    Edges for Aura X5 Pro: [('Aura X5', 'Aura X5 Pro'), ('Aura X5 Pro', 'Phone'), ('Aura X5 Pro', 'Mobile Phones'), ('Aura X5 Pro', 'Aura X5'), ('Aura X5 Pro', 'Home')]
    
    Node Data for SnapShot Voyager Camera 3.0: {'name': 'SnapShot Voyager Camera 3.0', 'price': 249.99, 'weight': 350, 'features': 'Intuitive Interface: Navigate settings and modes effortlessly with a user-friendly touchscreen and simple controls. High-Resolution Sensor: Capture sharp, vibrant photos and videos with a 24-megapixel sensor. Optical Image Stabilization: Reduce blur from camera shake for clear images even in low light or while in motion. 4K Video Recording: Record smooth, high-definition video at 4K resolution. Built-in Wi-Fi: Easily transfer photos and videos to your smartphone or tablet for sharing. Versatile Shooting Modes: Choose from a variety of modes, including portrait, landscape, sports, and night mode. Long Battery Life: Enjoy extended shooting sessions with a long-lasting rechargeable battery.'}
    
    Edges for SnapShot Voyager Camera 3.0: [('SnapShot Voyager Lens Hood', 'SnapShot Voyager Camera 3.0'), ('SnapShot Voyager Remote Shutter Release', 'SnapShot Voyager Camera 3.0'), ('SnapShot Voyager Camera 3.0', 'Camera'), ('SnapShot Voyager Camera 3.0', 'Home'), ('SnapShot Voyager Camera 3.0', 'SnapShot Voyager Remote Shutter Release'), ('SnapShot Voyager Camera 3.0', 'SnapShot Voyager Lens Hood'), ('SnapShot Voyager Camera 3.0', 'Photography')]
    
    Node Data for AuraBook Air: {'name': 'AuraBook Air', 'price': 999, 'weight': 2.5, 'features': 'Ultra-lightweight design for maximum portability. Brilliant 13.3-inch Full HD Display. Fast and responsive performance. Long-lasting battery life for all-day use. Integrated HD webcam for video conferencing. Sleek, modern design.'}
    
    Edges for AuraBook Air: [('AuraBook Air', 'Computer'), ('AuraBook Air', 'Office'), ('AuraBook Air', 'Laptops'), ('AuraBook Air', 'Home')]
    
    Node Data for SkyHawk Zephyr Drone: {'name': 'SkyHawk Zephyr Drone', 'price': 0, 'weight': 0, 'features': 'Simple Controls: Beginner friendly and intuitive controls, plus automatic takeoff and landing. Tough Build: Designed to handle rookie mistakes, thanks to its robust construction. Capture Memories: Record crisp HD photos and videos from above. Extended Fun: Enjoy up to 15 minutes of flight time per charge. Worry-Free Flying: Free Fly mode lets you fly without directional concerns.'}
    
    Edges for SkyHawk Zephyr Drone: [('SkyHawk Zephyr 2.0 - Reach New Heights', 'SkyHawk Zephyr Drone'), ('SkyHawk Zephyr Drone', 'Videography'), ('SkyHawk Zephyr Drone', 'SkyHawk Zephyr Propeller Guards'), ('SkyHawk Zephyr Drone', 'Drone'), ('SkyHawk Zephyr Propeller Guards', 'SkyHawk Zephyr Drone'), ('SkyHawk Zephyr Extended Battery', 'SkyHawk Zephyr Drone'), ('SkyHawk Zephyr Drone', 'SkyHawk Zephyr Extended Battery'), ('SkyHawk Zephyr Drone', 'Home'), ('SkyHawk Zephyr Drone', 'SkyHawk Zephyr 2.0 - Reach New Heights'), ('SkyHawk Zephyr Drone', 'Photography')]
    
    Node Data for SkyHawk Zephyr Extended Battery: {'name': 'SkyHawk Zephyr Extended Battery', 'price': 29.99, 'weight': 70, 'features': 'Increased Capacity: Enjoy up to 25 minutes of flight time on a single charge, a 67% increase over the standard battery. Easy Installation: Seamlessly swap out with the original battery in seconds. Safe and Reliable: Built to the same high-quality standards as the SkyHawk Zephyr drone.'}
    
    Edges for SkyHawk Zephyr Extended Battery: [('SkyHawk Zephyr Drone', 'SkyHawk Zephyr Extended Battery'), ('SkyHawk Zephyr Extended Battery', 'Videography'), ('SkyHawk Zephyr Extended Battery', 'Photography'), ('SkyHawk Zephyr Extended Battery', 'SkyHawk Zephyr Drone')]
    
    Node Data for SkyHawk Zephyr 2.0 - Reach New Heights: {'name': 'SkyHawk Zephyr 2.0 - Reach New Heights', 'price': 199.99, 'weight': 250, 'features': '4K Camera: Capture breathtaking aerial footage in stunning 4K resolution with enhanced image stabilization. Extended Flight Time: Enjoy up to 20 minutes of flight time on a single charge. Increased Range: Fly farther with an extended control range of up to 1.2km (3/4 mile). Intelligent Flight Modes: Explore creative filming options with Follow Me, Orbit, and Waypoint modes. GPS-Assisted Flight: Benefit from precise positioning and enhanced safety features like Return-to-Home. Upgraded Motors: Experience smoother, more responsive flight and increased agility. Streamlined Design: A sleek and aerodynamic design for improved flight performance.'}
    
    Edges for SkyHawk Zephyr 2.0 - Reach New Heights: [('SkyHawk Zephyr Drone', 'SkyHawk Zephyr 2.0 - Reach New Heights'), ('SkyHawk Zephyr 2.0 - Reach New Heights', 'Drone'), ('SkyHawk Zephyr 2.0 - Reach New Heights', 'Photography'), ('SkyHawk Zephyr 2.0 - Reach New Heights', 'SkyHawk Zephyr Drone'), ('SkyHawk Zephyr 2.0 - Reach New Heights', 'Home'), ('SkyHawk Zephyr 2.0 - Reach New Heights', 'Videography')]
    
    Node Data for  answer questions: {'name': ' answer questions', 'price': 0, 'weight': 0, 'features': ''}
    
    Edges for  answer questions: []
    
    Node Data for SkyHawk Zephyr Propeller Guards: {'name': 'SkyHawk Zephyr Propeller Guards', 'price': 14.99, 'weight': 20, 'features': 'Enhanced Safety: Prevent accidental damage to the propellers and surroundings during flight. Lightweight Design: Minimal impact on flight performance. Easy Installation: Snap on and off in seconds for quick and convenient use. Increased Durability: Provides an extra layer of protection for your drone.'}
    
    Edges for SkyHawk Zephyr Propeller Guards: [('SkyHawk Zephyr Drone', 'SkyHawk Zephyr Propeller Guards'), ('SkyHawk Zephyr Propeller Guards', 'Photography'), ('SkyHawk Zephyr Propeller Guards', 'SkyHawk Zephyr Drone'), ('SkyHawk Zephyr Propeller Guards', 'Videography')]
    
    Node Data for ChromaJet Starter Bundle: {'name': 'ChromaJet Starter Bundle', 'price': 528, 'weight': 12, 'features': 'Complete Starter Package: Includes printer and cleaning kit for immediate use. Professional-Grade Quality: Produce high-resolution prints with exceptional color accuracy. User-Friendly Interface: Intuitive controls for easy operation, even for beginners. Versatile Media Handling: Supports a wide range of paper types and sizes. Durable Construction: Built to last, ensuring years of reliable performance.'}
    
    Edges for ChromaJet Starter Bundle: [('ChromaJet Starter Bundle', 'Printing')]


Congratulations! It works.  

---  

## Generate Answer  

The final step is to generate an answer using the LLM.  

### Define a Prompt  
First, let's define a prompt template for the LLM to generate an answer as follows.


```python
>>> PROMPTS = """---Role---
... 
... You are a helpful assistant responding to questions about data in the tables provided.
... 
... 
... ---Goal---
... 
... Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
... If you don't know the answer, just say so. Do not make anything up.
... Do not include information where the supporting evidence for it is not provided.
... 
... ---Target response length and format---
... 
... {response_type}
... 
... 
... ---Data tables---
... 
... {context_data}
... 
... 
... ---Goal---
... 
... Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
... 
... If you don't know the answer, just say so. Do not make anything up.
... 
... Do not include information where the supporting evidence for it is not provided.
... 
... 
... ---Target response length and format---
... 
... {response_type}
... 
... Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
... """
```

### Define a Function to Generate Answer

Then let's define a `query` function that integrates the context builder and OpenAIChat to process user queries. This function retrieves relevant context from the graph, constructs a system prompt, and generates a response using the LLM.


```python
>>> from tigergraphx.graphrag import BaseContextBuilder
>>> from tigergraphx.llm import OpenAIChat
>>> async def query(
...     query: str,
...     openai_chat: OpenAIChat,
...     context_builder: BaseContextBuilder,
...     top_k: int = 10,
...     only_need_context: bool = False,
...     response_type: str = "Multiple Paragraphs",
... ) -> str:
...     """
...     Perform a local search using the context builder and return the result.
...     """
...     # Generate context using the local context builder
...     context = await context_builder.build_context(
...         query,
...         k=top_k,
...     )
...     if only_need_context:
...         if not isinstance(context, str):
...             raise TypeError("Expected `context` to be an instance of str.")
...         return context
... 
...     # Validate that context exists
...     if not context:
...         return "Apologies, but I couldn't provide an answer as no relevant context was found for your query."
... 
...     # Construct the system prompt using the context
...     system_prompt = PROMPTS.format(context_data=context, response_type=response_type)
... 
...     # Perform the query using OpenAIChat
...     try:
...         response = await openai_chat.chat(
...             [
...                 {"role": "system", "content": system_prompt},
...                 {"role": "user", "content": query},
...             ]
...         )
...         return response
...     except Exception:
...         return "An error occurred while processing the query."
```

### Run the Function to Generate an Answer  
Great job! The final step is to provide a question and call the function to generate an answer.


```python
>>> result = await query(
...     query="I am looking for a begginer drone. Please give me some recommendations.",
...     openai_chat=openai_chat,
...     context_builder=context_builder,
...     only_need_context=False,
... )
>>> print(result)
```

    2025-03-28 15:15:53,971 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-03-28 15:16:04,309 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    ### Recommendations for Beginner Drones
    
    When it comes to selecting a beginner-friendly drone, it's essential to consider ease of use, durability, and features that enhance the flying experience. Based on available data, here are two excellent options for beginner drones:
    
    #### 1. SkyHawk Zephyr Drone
    
    **Price:** $0 (likely indicating it comes free with a package or promotional offer)
    
    **Features:**
    - **Simple Controls:** This drone is designed with beginner-friendly and intuitive controls, plus it includes automatic takeoff and landing capabilities to ease new users into flying.
    - **Robust Build:** The SkyHawk Zephyr is constructed to withstand typical beginner mistakes, making it durable and reliable for novice pilots.
    - **Photography and Videography:** Equipped with an HD camera, it allows users to capture crisp photos and videos from above, appealing to those interested in aerial photography.
    - **Flight Time:** Users can enjoy approximately 15 minutes of flight time per charge, giving a decent amount of flying enjoyment.
    
    Given its features, the SkyHawk Zephyr Drone is a fantastic option for newcomers to the world of drones, providing an intuitive flying experience while delivering quality content during flights.
    
    #### 2. SkyHawk Zephyr 2.0 - Reach New Heights
    
    **Price:** $199.99
    
    **Features:**
    - **4K Camera:** This drone boasts a high-quality 4K camera, perfect for capturing stunning aerial footage, appealing to users looking to create high-definition content.
    - **Extended Flight Time:** With up to 20 minutes of flight time on a single charge, users can enjoy longer flying sessions.
    - **Intelligent Flight Modes:** It offers advanced flight options such as Follow Me, Orbit, and Waypoint modes for creative filming, making it great for users interested in exploring versatile filming capabilities.
    - **GPS-Assisted Flight:** Features like Return-to-Home enhance safety for beginners, ensuring that even those new to flying can have a worry-free experience.
    
    The SkyHawk Zephyr 2.0 presents a step up in features from the base model. It's suitable for beginners who want to grow their skills while still having access to advanced features for creative pursuits.
    
    ### Conclusion
    
    Both the SkyHawk Zephyr Drone and the SkyHawk Zephyr 2.0 are excellent choices for beginner drone enthusiasts. The former is particularly good for pure novices due to its straightforward controls and robust build, while the latter provides additional features that enhance the flying experience as users become more comfortable. When selecting a drone, consider your specific needs, such as the desire for photography or content creation, and choose the model that aligns best with those interests.


---

## Reset

After completing the query, it is recommended to clean up the environment by removing the graph you created. You can drop the graph by running the following single line of code.


```python
>>> G.drop_graph()
```

    2025-03-28 15:20:17,365 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: RetailGraph...
    2025-03-28 15:20:22,112 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## What’s Next?

- [API Reference](../reference/introduction.md): Dive deeper into TigerGraphX APIs.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
