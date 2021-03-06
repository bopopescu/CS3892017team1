# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Promotes Cloud SQL read replica to a stand-alone instance."""

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


class _BasePromoteReplica(object):
  """Promotes Cloud SQL read replica to a stand-alone instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument('replica',
                        completion_resource='sql.instances',
                        help='Cloud SQL read replica ID.')


@base.ReleaseTracks(base.ReleaseTrack.GA)
class PromoteReplica(_BasePromoteReplica, base.Command):
  """Promotes Cloud SQL read replica to a stand-alone instance."""

  def Run(self, args):
    """Promotes Cloud SQL read replica to a stand-alone instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      promote-replica operation if the promote-replica was successful.
    Raises:
      HttpException: An HTTP error response was received while executing api
          request.
      ToolException: An error other than an HTTP error occured while executing
          the command.
    """
    client = api_util.SqlClient(api_util.API_VERSION_FALLBACK)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    validate.ValidateInstanceName(args.replica)
    instance_ref = client.resource_parser.Parse(
        args.replica,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances')

    console_io.PromptContinue(
        message='Once the read replica has been promoted to a stand-alone '
        'instance it cannot be converted back.',
        default=True,
        cancel_on_no=True)

    result = sql_client.instances.PromoteReplica(
        sql_messages.SqlInstancesPromoteReplicaRequest(
            project=instance_ref.project,
            instance=instance_ref.instance))
    operation_ref = client.resource_parser.Create(
        'sql.operations',
        operation=result.operation,
        project=instance_ref.project,
        instance=instance_ref.instance,
    )

    if args.async:
      return sql_client.operations.Get(
          sql_messages.SqlOperationsGetRequest(
              project=operation_ref.project,
              instance=operation_ref.instance,
              operation=operation_ref.operation))

    operations.OperationsV1Beta3.WaitForOperation(
        sql_client, operation_ref, 'Promoting Cloud SQL replica')

    log.status.write(
        'Promoted [{instance}].\n'.format(instance=instance_ref))


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class PromoteReplicaBeta(_BasePromoteReplica, base.Command):
  """Promotes Cloud SQL read replica to a stand-alone instance."""

  def Run(self, args):
    """Promotes Cloud SQL read replica to a stand-alone instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      promote-replica operation if the promote-replica was successful.
    Raises:
      HttpException: An HTTP error response was received while executing api
          request.
      ToolException: An error other than an HTTP error occured while executing
          the command.
    """
    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    validate.ValidateInstanceName(args.replica)
    instance_ref = client.resource_parser.Parse(
        args.replica,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances')

    console_io.PromptContinue(
        message='Once the read replica has been promoted to a stand-alone '
        'instance it cannot be converted back.',
        default=True,
        cancel_on_no=True)

    result = sql_client.instances.PromoteReplica(
        sql_messages.SqlInstancesPromoteReplicaRequest(
            project=instance_ref.project,
            instance=instance_ref.instance))
    operation_ref = client.resource_parser.Create(
        'sql.operations',
        operation=result.name,
        project=instance_ref.project)

    if args.async:
      return sql_client.operations.Get(
          sql_messages.SqlOperationsGetRequest(
              project=operation_ref.project,
              instance=operation_ref.instance,
              operation=operation_ref.operation))

    operations.OperationsV1Beta4.WaitForOperation(
        sql_client, operation_ref, 'Promoting Cloud SQL replica')

    log.status.write(
        'Promoted [{instance}].\n'.format(instance=instance_ref))
