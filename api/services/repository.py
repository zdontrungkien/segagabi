from bson import ObjectId
from pymongo.errors import WriteError

import api.main as api
from api.routers.exceptions import AlreadyExistsHTTPException


async def document_id_helper(document: dict) -> dict:
    document["id"] = document.pop("_id")
    return document


async def retrieve_document(document_id: str, collection: str) -> dict:
    """

    :param document_id:
    :param collection:
    :return:
    """
    document_filter = {"_id": ObjectId(document_id)}
    if document := await api.app.state.mongo_collection[collection].find_one(document_filter):
        return await document_id_helper(document)
    else:
        raise ValueError(f"No document found for {document_id=} in {collection=}")


async def create_document(document: dict, collection: str) -> dict:
    """

    :param document:
    :param collection:
    :return:
    """
    try:
        document = await api.app.state.mongo_collection[collection].insert_one(document)
        return await retrieve_document(document.inserted_id, collection)
    except WriteError:
        raise AlreadyExistsHTTPException(f"Document with {document.inserted_id=} already exists")


async def update_document(document_id: str, data: dict, collection: str) -> bool:
    """

    :param document_id:
    :param collection:
    :return:
    """
    document_filter = {"_id": ObjectId(document_id)}
    document = await api.app.state.mongo_collection[collection].find_one(document_filter)
    if document:
        document = api.app.state.mongo_collection[collection].update_one(
            document_filter,
            {"$set": data}
        )
        return True
    else:
        raise ValueError(f"No document found for {document_id=} in {collection=}")


async def delete_document(document_id: str, collection: str) -> dict:
    """

    :param document_id:
    :param collection:
    :return:
    """
    document_filter = {"_id": ObjectId(document_id)}
    if document := await api.app.state.mongo_collection[collection].find_one(document_filter):
        await api.app.state.mongo_collection[collection].delete_one(document_filter)
        return True
    else:
        raise ValueError(f"No document found for {document_id=} in {collection=}")


async def get_mongo_meta() -> dict:
    print('----------0--------')
    list_databases = await api.app.state.mongo_client.list_database_names()
    print('----------1--------')
    list_of_collections = {}
    for db in list_databases:
        list_of_collections[db] = await api.app.state.mongo_client[db].list_collection_names()
    print('----------2--------')
    mongo_meta = await api.app.state.mongo_client.server_info()
    print('----------3--------')
    return {"version": mongo_meta["version"], "databases": list_databases, "collections": list_of_collections}
