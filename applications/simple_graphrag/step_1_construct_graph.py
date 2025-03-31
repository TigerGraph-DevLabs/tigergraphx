# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import os
import asyncio
import aiofiles
import json

from tigergraphx.llm import OpenAIManager, OpenAIChat
from tigergraphx.vector_search import OpenAIEmbedding

from graph_schema import graph_schema

# System Prompt
SYSTEM_PROMPT = "You are a helpful assistant."


def load_documents(path):
    """Load text documents from subdirectories."""
    documents = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):  # Only process text files
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    documents.append(f.read())
    return documents


def generate_prompt(document):
    """Generate a structured prompt for OpenAI based on document content."""
    return f"""
You are an AI that extracts structured graph data from a given document, strictly following this schema:

{str(graph_schema)}

### **Extraction Rules:**
- Extract the exact `name` of each entity as it appears in the document. **Do not modify, expand, or infer names.**
- The `Segment` can only be one of: `"Home"`, `"Office"`, or `"Fitness"`. If a `Segment` is not explicitly mentioned, **do not assign one**.
- Every `Product` must have:
  - A `features` property describing key characteristics.
  - A `price` (as a numeric value, not a string).
  - A `weight` (as a numeric value, not a string).
- Do not infer missing information. Only extract what is explicitly stated in the document.
- **Do not create relationships with `null` targets.** If a valid target is not available, omit the relationship from the output.
- If a `Category` is not mentioned explicitly, **do not generate it**.
- If a `Bundle` is not mentioned explicitly, **do not generate it**.
- If a `Deal` is not mentioned explicitly, **do not generate it**.
- Maintain consistent formatting for all properties.
- **Do not add comments to the JSON output**.
- If a field is missing or the value is unknown, set it as `""`. 

---

### **Example Document & Expected Output:**

#### **Document:**
```
Product: SkyHawk Zephyr Drone
Price: $129.99
Weight: 220g (7.8 oz)
The SkyHawk Zephyr is the perfect drone for beginners. It's built for effortless flying, offering a smooth and enjoyable experience from the moment you unpack it.

Features:
- Simple Controls: Beginner friendly and intuitive controls, plus automatic takeoff and landing.
- Tough Build: Designed to handle rookie mistakes, thanks to its robust construction.
- Capture Memories: Record crisp HD photos and videos from above.
- Extended Fun: Enjoy up to 15 minutes of flight time per charge.
- Worry-Free Flying: Free Fly mode lets you fly without directional concerns.

Take your first flight with the SkyHawk Zephyr and discover the joy of aerial views!

Category: Drone
Segment: ['Home']
Tags: ['Photography', 'Videography']
```

#### **Expected Output (JSON format):**
```json
{{
  "nodes": [
    {{"id": "SkyHawk Zephyr Drone", "type": "Product", "properties": {{"name": "SkyHawk Zephyr Drone", "price": 129.99, "weight": 220, "features": "Simple Controls: Beginner friendly and intuitive controls, plus automatic takeoff and landing. Tough Build: Designed to handle rookie mistakes, thanks to its robust construction. Capture Memories: Record crisp HD photos and videos from above. Extended Fun: Enjoy up to 15 minutes of flight time per charge. Worry-Free Flying: Free Fly mode lets you fly without directional concerns."}}}},
    {{"id": "Drone", "type": "Category", "properties": {{"name": "Drone"}}}},
    {{"id": "Photography", "type": "Tag", "properties": {{"name": "Photography"}}}},
    {{"id": "Videography", "type": "Tag", "properties": {{"name": "Videography"}}}},
    {{"id": "Home", "type": "Segment", "properties": {{"name": "Home"}}}}
  ],
  "relationships": [
    {{"source": "SkyHawk Zephyr Drone", "target": "Drone", "type": "In_Category"}},
    {{"source": "SkyHawk Zephyr Drone", "target": "Photography", "type": "Tagged_With"}},
    {{"source": "SkyHawk Zephyr Drone", "target": "Videography", "type": "Tagged_With"}},
    {{"source": "SkyHawk Zephyr Drone", "target": "Home", "type": "In_Segment"}}
  ]
}}
```

---

### **Now process the following document:**
{document}

**Follow the exact JSON structure as shown above.**
"""


async def process_document(openai_chat, document):
    """Process a single document asynchronously and return structured data."""
    response = await openai_chat.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": generate_prompt(document)},
        ]
    )
    return response


async def write_csv(filename, data_list, data_type):
    """Write nodes or relationships to a CSV file asynchronously."""
    async with aiofiles.open(filename, "w", newline="") as f:
        if data_type == "node":
            all_keys = sorted(
                {key for node in data_list for key in node["properties"].keys()}
            )
            await f.write(",".join(["id", "type"] + all_keys) + "\n")

            for node in data_list:
                row = [node["id"], node["type"]] + [
                    f'"{str(node["properties"].get(key, ""))}"'
                    if "," in str(node["properties"].get(key, ""))
                    else str(node["properties"].get(key, ""))
                    for key in all_keys
                ]
                await f.write(",".join(row) + "\n")

        elif data_type == "relationship":
            await f.write("source,target\n")
            for rel in data_list:
                await f.write(f"{rel['source']},{rel['target']}\n")


async def process_all_documents(
    openai_chat: OpenAIChat,
    openai_embedding: OpenAIEmbedding,
    document_lists,
    output_dir,
):
    """Process all documents asynchronously and write results to CSV."""
    os.makedirs(output_dir, exist_ok=True)

    tasks = [
        asyncio.create_task(process_document(openai_chat, doc))
        for doc in document_lists
    ]
    responses = await asyncio.gather(*tasks)

    # Flatten responses and parse JSON
    graph_documents = []
    for response in responses:
        cleaned_response = response.strip("`").replace(
            "json\n", ""
        )  # Remove backticks and json tag
        try:
            parsed_data = json.loads(cleaned_response)
            graph_documents.append(parsed_data)
        except json.JSONDecodeError:
            print(f"Error parsing JSON: {cleaned_response}")  # Debugging
            continue  # Skip invalid JSON

    # Organize nodes and relationships
    nodes, relationships = {}, {}

    for doc in graph_documents:
        for node in doc.get("nodes", []):
            node_type = node["type"]
            nodes.setdefault(node_type, []).append(node)

        for rel in doc.get("relationships", []):
            rel_type = rel["type"]
            relationships.setdefault(rel_type, []).append(rel)

    # Add embeddings to the graph documents for Product nodes
    for node in nodes.get("Product", []):
        if "features" in node.get("properties", {}):
            embedding = await openai_embedding.generate_embedding(
                node["properties"]["features"]
            )
            node["properties"]["embedding"] = " ".join(map(str, embedding))

    # Write CSV files
    await asyncio.gather(
        *[
            asyncio.create_task(
                write_csv(
                    os.path.join(output_dir, f"nodes_{node_type.lower()}.csv"),
                    node_list,
                    "node",
                )
            )
            for node_type, node_list in nodes.items()
        ],
        *[
            asyncio.create_task(
                write_csv(
                    os.path.join(output_dir, f"edges_{rel_type.lower()}.csv"),
                    rel_list,
                    "relationship",
                )
            )
            for rel_type, rel_list in relationships.items()
        ],
    )


def main():
    """Main entry point for processing documents and extracting graph data."""

    document_lists = load_documents("data/retaildata")

    openai = OpenAIManager(config={})
    openai_chat = OpenAIChat(openai, config={"model": "gpt-4o-mini"})
    openai_embedding = OpenAIEmbedding(
        openai, config={"model": "text-embedding-3-small"}
    )
    output_dir = "data/output"
    asyncio.run(
        process_all_documents(openai_chat, openai_embedding, document_lists, output_dir)
    )


if __name__ == "__main__":
    main()
