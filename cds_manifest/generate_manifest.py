#!/usr/bin/env python

import csv
import os
import sys
import uuid

import synapseclient
from synapseclient.core.exceptions import SynapseHTTPError


SYN = synapseclient.login(silent=True)

COLNAMES = [
    "file name",
    "file id",
    "acl value",
    "file size",
    "md5 hash",
    "file uri"
]


def main():

    with open(sys.argv[1]) as i_f, open(sys.argv[2], "w") as o_f, open(sys.argv[3], "w") as e_f:

        # Prepare CSV writer
        csv_writer = csv.DictWriter(o_f, fieldnames=COLNAMES)
        csv_writer.writeheader()

        # Iterate over Synapse IDs
        for row in i_f:
            syn_id = row.rstrip("\n")
            syn_info = get_entity_info(syn_id)
            if "file uri" in syn_info:
                csv_writer.writerow(syn_info)
            else:
                e_f.write(row)


def get_entity_info(entity_id):

    # Get list of file handles, but extract the one
    try:
        response = SYN.restGET(f"/entity/{entity_id}/filehandles")
    except SynapseHTTPError as e:
        if "does not have a file handle" in str(e):
            return dict()
        raise e
    file_handles = response["list"]
    assert (
        len(file_handles) == 1
    ), f"Check what's going on with {entity_id}: {file_handles}"
    file_handle = file_handles[0]

    # Confirm file handle type (AWS)
    file_handle_type = file_handle["concreteType"].split(".")[-1]
    assert (
        file_handle_type in {"S3FileHandle", "GoogleCloudFileHandle"}
    ), f"Check what's going on with {entity_id}: {file_handle}"

    bucket_name =   file_handle["bucketName"]
    object_key =    file_handle["key"]
    uri_scheme =    "s3" if file_handle_type == "S3FileHandle" else "gs"
    object_uri =    f"{uri_scheme}://{bucket_name}/{object_key}"

    entity_info = {
        "file name":    os.path.basename(file_handle["key"]),
        "file id":      uuid.uuid4(),
        "acl value":    "",
        "file size":    file_handle["contentSize"],
        "md5 hash":     file_handle["contentMd5"],
        "file uri":     object_uri,
    }

    return entity_info


if __name__ == "__main__":
    main()
