#!/bin/bash
sshfs ${DVC_REMOTE_USER}@cic-qbo.hpc.uio.no:/storage/qbo/cm-group/dvc_storage/iam_compact $(dirname $0)/dvc_sshfs_remote/

