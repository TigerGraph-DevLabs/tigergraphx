# Supporting Microsoft’s GraphRAG: Part 5 - Query and Evaluation
In the previous section, we introduct how to perform retrieve and build context, also integegration with LLM.
Since there are a lot of code, we will not show them in Jupyter Notework. Instead, we put all the code under 
[folder](https://github.com/tigergraph/tigergraphx/blob/main/applications/msft_graphrag). And you can run them directly using shell command.

---

## Query
We define a POE task named `graphrag_query` as `python -m applications.msft_graphrag.query.main`.
By running the command below, you can query GraphRAG. The mode can be either **local** or **global**.


```python
!poe graphrag_query --mode local --query "where is the world's largest man made lake"
```

    [37mPoe =>[0m [94mpython -m applications.msft_graphrag.query.main --mode local --query 'where is the world'"'"'s largest man made lake'[0m
    2025-02-28 22:42:43,708 - datasets - INFO - PyTorch version 2.6.0 available.
    2025-02-28 22:42:43,919 - applications.msft_graphrag.query.graphrag - INFO - Initializing GraphRAG with schema_path: applications/msft_graphrag/query/resources/graph_schema.yaml, loading_job_path: applications/msft_graphrag/query/resources/loading_job_config.yaml, settings_path: applications/msft_graphrag/query/resources/settings.yaml
    2025-02-28 22:42:44,157 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:42:44,158 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:42:44,158 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:42:44,158 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:42:46,028 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:42:47,809 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:42:52,001 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    ------------------- Query Result:  -------------------
    ## Overview of the World's Largest Man-Made Lake
    
    The world's largest man-made lake is Lake Kariba, located on the border between Zambia and Zimbabwe. Created in the 1950s by the construction of the Kariba Dam on the Zambezi River, Lake Kariba spans an impressive surface area of approximately 5,400 square kilometers (2,080 square miles) and holds a massive volume of water. The lake was formed to provide hydroelectric power and is critical for electricity generation in the region.
    
    ## Significance and Features
    
    Lake Kariba is not only significant for its size but also for its ecological and economic importance. The lake supports a diverse range of wildlife and aquatic species, which contributes to local fisheries and tourism. It is a vital resource for both Zambia and Zimbabwe, impacting local communities and economies through fishing, tourism, and hydroelectricity. Furthermore, it serves as a recreational area, attracting visitors for activities such as boating, fishing, and wildlife viewing.
    
    ## Historical Context
    
    The creation of Lake Kariba had profound implications for the area, displacing communities and affecting local ecosystems. The dam construction required substantial engineering efforts and investment, which reflected the ambitions of both nations to enhance their energy capacities and economic development. Today, Lake Kariba continues to be a focal point in regional discussions about resource management and sustainable development.
    
    In summary, Lake Kariba stands out as a remarkable feat of engineering and a crucial environmental asset, reflecting both the triumphs and challenges of human intervention in natural landscapes.


---

## Evaluation
We define a POE task named `graphrag_evaluation` as `python -m applications.msft_graphrag.query.evaluation`.  
Run the command below to evaluate GraphRAG.


```python
!poe graphrag_evaluation --mode local
```

    [37mPoe =>[0m [94mpython -m applications.msft_graphrag.query.evaluation --mode local[0m
    2025-02-28 22:43:27,683 - applications.msft_graphrag.query.graphrag - INFO - Initializing GraphRAG with schema_path: applications/msft_graphrag/query/resources/graph_schema.yaml, loading_job_path: applications/msft_graphrag/query/resources/loading_job_config.yaml, settings_path: applications/msft_graphrag/query/resources/settings.yaml
    2025-02-28 22:43:27,882 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:27,882 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:27,882 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:27,882 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:28,629 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:30,423 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:30,423 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:30,423 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:30,423 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:30,779 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:32,210 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:43:37,740 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:43:37,750 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:37,750 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:37,750 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:37,750 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:38,458 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:39,940 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:39,940 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:39,940 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:39,940 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:40,711 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:42,074 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:43:49,618 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:43:49,621 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:49,621 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:49,621 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:49,621 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:50,029 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:51,468 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:51,468 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:51,468 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:51,468 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:52,074 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:53,478 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:43:56,219 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:43:56,221 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:56,221 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:56,221 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:56,221 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:56,685 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:43:58,223 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:43:58,223 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:43:58,224 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:43:58,224 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:43:58,938 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:00,406 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:06,219 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:06,222 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:06,223 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:06,223 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:06,223 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:06,924 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:08,399 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:08,399 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:08,399 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:08,399 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:09,484 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:10,911 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:14,399 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:14,402 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:14,402 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:14,402 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:14,402 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:15,117 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:16,606 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:16,606 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:16,606 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:16,606 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:17,673 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:19,097 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:23,102 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:23,105 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:23,105 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:23,105 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:23,105 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:23,412 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:24,914 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:24,915 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:24,915 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:24,915 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:25,358 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:26,721 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:33,752 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:33,754 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:33,754 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:33,754 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:33,755 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:34,163 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:35,493 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:35,494 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:35,494 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:35,494 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:36,132 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:37,525 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:42,253 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:42,258 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:42,258 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:42,258 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:42,258 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:42,970 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:44,329 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:44,329 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:44,329 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:44,329 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:44,754 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:46,112 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:44:51,878 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:44:51,881 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=True, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:51,882 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:51,882 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:51,882 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:52,596 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:54,463 - applications.msft_graphrag.query.graphrag - INFO - Executing query with parameters: QueryParam(mode='local', only_need_context=False, response_type='Multiple Paragraphs', top_k=20)
    2025-02-28 22:44:54,463 - applications.msft_graphrag.query.graphrag - INFO - Retrieving existing event loop.
    2025-02-28 22:44:54,463 - applications.msft_graphrag.query.graphrag - INFO - Starting asynchronous query execution.
    2025-02-28 22:44:54,463 - applications.msft_graphrag.query.graphrag - INFO - Performing local query with top_k: 20
    2025-02-28 22:44:54,952 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:44:56,477 - applications.msft_graphrag.query.graphrag - INFO - Executing final query with OpenAIChat.
    2025-02-28 22:45:03,859 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,727 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,728 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,746 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,750 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,805 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:06,865 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:07,240 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:07,242 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:07,855 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:08,263 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:   2%|▊                               | 1/40 [00:03<02:24,  3.71s/it]2025-02-28 22:45:08,287 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:08,288 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:08,289 - openai._base_client - INFO - Retrying request to /chat/completions in 0.459660 seconds
    2025-02-28 22:45:08,290 - openai._base_client - INFO - Retrying request to /chat/completions in 0.388346 seconds
    2025-02-28 22:45:08,290 - openai._base_client - INFO - Retrying request to /chat/completions in 0.448891 seconds
    2025-02-28 22:45:08,687 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:09,167 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:09,564 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:09,732 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:09,761 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,156 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,516 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,902 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  18%|█████▌                          | 7/40 [00:06<00:27,  1.19it/s]2025-02-28 22:45:10,945 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,946 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,948 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,949 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,950 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:10,968 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:11,438 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:12,156 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  20%|██████▍                         | 8/40 [00:07<00:30,  1.05it/s]2025-02-28 22:45:12,170 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:12,171 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:12,183 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:12,197 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:12,973 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:13,382 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  25%|███████▊                       | 10/40 [00:08<00:23,  1.25it/s]2025-02-28 22:45:13,392 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:13,394 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:13,751 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,050 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  32%|██████████                     | 13/40 [00:09<00:13,  1.94it/s]2025-02-28 22:45:14,065 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,065 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,468 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,920 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  38%|███████████▋                   | 15/40 [00:10<00:12,  2.05it/s]2025-02-28 22:45:14,930 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,932 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:14,989 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:15,691 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:15,984 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,213 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,232 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,438 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,531 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,541 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:16,687 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:17,172 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:17,670 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  45%|█████████████▉                 | 18/40 [00:13<00:14,  1.51it/s]2025-02-28 22:45:17,677 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:17,679 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:17,680 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:17,843 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:18,300 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:18,673 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  52%|████████████████▎              | 21/40 [00:14<00:10,  1.84it/s]2025-02-28 22:45:18,683 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:18,843 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:20,041 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:20,042 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:20,257 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:20,398 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:20,741 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:21,167 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  62%|███████████████████▍           | 25/40 [00:16<00:09,  1.54it/s]2025-02-28 22:45:21,171 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:21,171 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:21,678 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-02-28 22:45:22,227 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    Evaluating:  65%|████████████████████▏          | 26/40 [00:17<00:10,  1.34it/s]2025-02-28 22:45:22,293 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:22,905 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:23,653 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:24,195 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:25,160 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:27,874 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:28,438 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:29,971 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:43,271 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:46,457 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:46,546 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:51,377 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:52,397 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:56,874 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:45:57,277 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:46:04,407 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-02-28 22:46:05,299 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    Evaluating: 100%|███████████████████████████████| 40/40 [01:00<00:00,  1.52s/it]
    2025-02-28 22:46:06,104 - tigergraphx.graphrag.evaluation.ragas_evaluator - INFO - Evaluation results: {'answer_relevancy': 0.8074, 'faithfulness': 0.4920, 'llm_context_precision_with_reference': 0.4000, 'context_recall': 0.3000}


The final line displays the evaluation results:

`Evaluation results: {'answer_relevancy': 0.8074, 'faithfulness': 0.4920, 'llm_context_precision_with_reference': 0.4000, 'context_recall': 0.3000}`

---

## Reset

After completing the evaluation, it is recommended to clean up the environment by removing the previously created graphs.


```python
!poe graphrag_reset
```

    [37mPoe =>[0m [94mpython -m applications.msft_graphrag.query.reset[0m
    2025-02-28 22:49:46,395 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: GraphRAG...
    2025-02-28 22:49:50,405 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## What’s Next?

- [API Reference](../../reference/introduction): Dive deeper into TigerGraphX APIs.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
