# Copyright 2014 Google Inc. All Rights Reserved.
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

"""The gcloud dns command group."""

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.core import resources


@base.ReleaseTracks(base.ReleaseTrack.GA)
class DNS(base.Group):
  """Manage your Cloud DNS managed-zones and record-sets.

  The gcloud dns command group lets you create and manage DNS zones and
  their associated records on Google Cloud DNS.

  Cloud DNS is a scalable, reliable and managed authoritative DNS service
  running on the same infrastructure as Google. It has low latency, high
  availability and is a cost-effective way to make your applications and
  services available to your users.

  More information on Cloud DNS can be found here:
  https://cloud.google.com/dns and detailed documentation can be found
  here: https://cloud.google.com/dns/docs/

  ## EXAMPLES

  To see how to create and maintain managed-zones, run:

    $ {command} managed-zones --help

  To see how to maintain the record-sets within a managed-zone, run:

    $ {command} record-sets --help

  To display Cloud DNS related information for your project, run:

    $ {command} project-info describe --help
  """

  def Filter(self, context, args):
    context['dns_client'] = apis.GetClientInstance('dns', 'v1')
    context['dns_messages'] = apis.GetMessagesModule('dns', 'v1')
    context['dns_resources'] = resources.REGISTRY

    return context