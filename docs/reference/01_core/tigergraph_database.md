# TigerGraphDatabase

## Overview

::: tigergraphx.core.tigergraph_database.TigerGraphDatabase
    options:
        members: false

## Constructor

::: tigergraphx.core.tigergraph_database.TigerGraphDatabase.__init__

For details on setting the TigerGraph connection configuration, please refer to [\_\_init\_\_](graph.md#tigergraphx.core.graph.Graph.__init__).

**Examples:**

## Admin Operations

::: tigergraphx.core.TigerGraphDatabase.ping

**Examples:**

```python
>>> from tigergraphx import TigerGraphDatabase
>>> db = TigerGraphDatabase()
>>> print(db.ping())
pong
```

## GSQL Operations

::: tigergraphx.core.TigerGraphDatabase.gsql

**Examples:**

```python
>>> from tigergraphx import TigerGraphDatabase
>>> db = TigerGraphDatabase()
>>> print(db.gsql("LS"))
---- Global vertices, edges, and all graphs
Vertex Types: 
Edge Types: 

Graphs: 
Jobs: 
Packages: 
  - Package gds
JSON API version: v2
Syntax version: v2
```

## Data Source Operations

::: tigergraphx.core.TigerGraphDatabase.create_data_source

**Example of Creating, Updating, Getting and Dropping a Data Source:**

```python
>>> from tigergraphx import TigerGraphDatabase
>>> db = TigerGraphDatabase()
>>> data_source_name = "tmp_data_source"
>>> result = db.create_data_source(
...     name=data_source_name,
...     data_source_type="s3",
...     access_key="",
...     secret_key="",
...     extra_config={
...         "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
...     },
... )
>>> print(result)
Data source tmp_data_source is created
>>> result = db.get_data_source(data_source_name)
>>> print(result)
{'name': 'tmp_data_source', 'type': 'S3', 'content': {'file.reader.settings.fs.s3a.aws.credentials.provider': 'org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider', 'access.key': 'none', 'secret.key': 'none', 'type': 's3'}}
>>> result = db.update_data_source(
...     name=data_source_name,
...     data_source_type="s3",
...     access_key="123",
...     secret_key="456",
...     extra_config={
...         "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
...     },
... )
>>> print(result)
Data source tmp_data_source is created
>>> result = db.get_data_source(data_source_name)
>>> print(result)
{'name': 'tmp_data_source', 'type': 'S3', 'content': {'file.reader.settings.fs.s3a.aws.credentials.provider': 'org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider', 'access.key': '123', 'secret.key': '456', 'type': 's3'}}
>>> result = db.drop_data_source(data_source_name)
>>> print(result)
Data source tmp_data_source is dropped.
```

::: tigergraphx.core.TigerGraphDatabase.update_data_source

**Examples:**

See the example in [create_data_source](#tigergraphx.core.TigerGraphDatabase.create_data_source).

::: tigergraphx.core.TigerGraphDatabase.get_data_source

**Examples:**

See the example in [create_data_source](#tigergraphx.core.TigerGraphDatabase.create_data_source).

::: tigergraphx.core.TigerGraphDatabase.drop_data_source

**Examples:**

See the example in [create_data_source](#tigergraphx.core.TigerGraphDatabase.create_data_source).

::: tigergraphx.core.TigerGraphDatabase.get_all_data_sources

**Example of Getting and Dropping all Data Sources:**

```python
>>> from tigergraphx import TigerGraphDatabase
>>> db = TigerGraphDatabase()
>>> data_source_name_1 = "tmp_data_source_1"
>>> result = db.create_data_source(
...     name=data_source_name_1,
...     data_source_type="s3",
...     access_key="",
...     secret_key="",
...     extra_config={
...         "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
...     },
... )
>>> print(result)
Data source tmp_data_source_1 is created
>>> data_source_name_2 = "tmp_data_source_2"
>>> result = db.create_data_source(
...     name=data_source_name_2,
...     data_source_type="s3",
...     access_key="",
...     secret_key="",
...     extra_config={
...         "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
...     },
... )
>>> print(result)
Data source tmp_data_source_2 is created
>>> result = db.get_all_data_sources()
>>> print(result)
[{'name': 'tmp_data_source_1', 'type': 'S3', 'content': {'file.reader.settings.fs.s3a.aws.credentials.provider': 'org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider', 'access.key': 'none', 'secret.key': 'none', 'type': 's3'}, 'isLocal': False}, {'name': 'tmp_data_source_2', 'type': 'S3', 'content': {'file.reader.settings.fs.s3a.aws.credentials.provider': 'org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider', 'access.key': 'none', 'secret.key': 'none', 'type': 's3'}, 'isLocal': False}]
>>> result = db.drop_all_data_sources()
>>> print(result)
All data sources is dropped successfully.
```

::: tigergraphx.core.TigerGraphDatabase.drop_all_data_sources

**Examples:**

See the example in [get_all_data_sources](#tigergraphx.core.TigerGraphDatabase.get_all_data_sources).

::: tigergraphx.core.TigerGraphDatabase.preview_sample_data

**Examples:**

```python
>>> from tigergraphx import TigerGraphDatabase
>>> db = TigerGraphDatabase()
>>> data_source_name = "tmp_data_source"
>>> result = db.create_data_source(
...     name=data_source_name,
...     data_source_type="s3",
...     access_key="",
...     secret_key="",
...     extra_config={
...         "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
...     },
... )
>>> print(result)
Data source tmp_data_source is created
>>> sample_path = "s3a://<YOUR_FILE_PATH>"
>>> preview_result = db.preview_sample_data(
...     path=sample_path,
...     data_source_type="s3",
...     data_source=data_source_name,
...     data_format="csv",
...     size=5,
...     has_header=True,
...     separator=",",
...     eol="\\n",
...     quote='"',
... )
>>> print(preview_result)
{'data': [['e4ed66aa-ec20-4ca6-b964-691f1b6c7bff', 'fde8014f-2202-42ca-b794-3836f4860c34', 'Garry', 'Taylor', '580', '2024-07-13 06:29:07.093715', 'relations1886@example.com', '+15619188445', 'Ames', 'United Arab Emirates', '79704', 'Oregon'], ['48a4b7c2-69e9-4e20-a096-a37f6e4d90f6', '48f037a7-77ba-4a6b-a98c-df39a91639f0', 'Kendall', 'Casey', '781', '2020-07-22 12:15:58.407056', 'implies2087@yahoo.com', '+16072840615', 'Brook Park', 'Timor-Leste', '94529', 'Florida'], ['4b10dd60-a0b6-43d8-8e71-b60e37b50e79', '6d483a3c-1d8a-463c-a1cd-7f09d2437f19', 'Alysa', 'Gilbert', '790', '2021-08-06 18:29:50.040560', 'televisions1888@duck.com', '+12561765695', 'Middletown', 'Curaçao', '71820', 'Michigan'], ['181fc56c-00fc-4d0d-8da5-28a00024f177', '369b271c-9437-4412-90d0-c75d10bbde44', 'Coralie', 'Alexander', '654', '2021-10-09 22:19:26.213723', 'greek1962@protonmail.com', '+19389607235', 'Niles', 'Hong Kong SAR China', '61987', 'Utah'], ['d3cd6fb1-61b1-4072-b160-079be29e77c4', '3116e7bc-4551-4c10-909f-883c727e7d3f', 'Benjamin', 'Barry', '741', '2024-02-09 04:58:03.182795', 'add1998@example.com', '+14179227097', 'Andover', 'Botswana', '82441', 'Kentucky']], 'json': False, 'header': ['account_ids', 'individual', 'first_name', 'last_name', 'credit_score', 'added_on', 'email', 'phone', 'city', 'country', 'zip', 'state']}
>>> result = db.drop_data_source(data_source_name)
>>> print(result)
Data source tmp_data_source is dropped.
```

