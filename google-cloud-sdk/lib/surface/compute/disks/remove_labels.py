# Copyright 2017 Google Inc. All Rights Reserved.
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
"""Command for removing labels from disks."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import labels_flags
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags
from googlecloudsdk.command_lib.util import labels_util


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class RemoveLabels(base.UpdateCommand):
  """Remove labels from Google Compute Engine persistent disk.

  *{command}* removes labels from a Google Compute Engine
  persistent disk.  For example:

    $ {command} example-disk --zone us-central1-a --labels=k0,k1

  will remove existing labels with key ``k0'' and ``k1'' from 'example-disk'.

  Labels can be used to identify the disk.
  """

  DISK_ARG = None

  @classmethod
  def Args(cls, parser):
    # Regional disk is in Alpha only.
    if cls.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      cls.DISK_ARG = disks_flags.MakeDiskArgZonalOrRegional(plural=False)
    else:
      cls.DISK_ARG = disks_flags.MakeDiskArg(plural=False)
    cls.DISK_ARG.AddArgument(parser)
    labels_flags.AddArgsForRemoveLabels(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client.apitools_client
    messages = holder.client.messages

    disk_ref = self.DISK_ARG.ResolveAsResource(
        args, holder.resources,
        scope_lister=flags.GetDefaultScopeLister(holder.client))

    remove_labels = labels_util.GetUpdateLabelsDictFromArgs(args)

    if disk_ref.Collection() == 'compute.disks':
      service = client.disks
      request_type = messages.ComputeDisksGetRequest
    elif disk_ref.Collection() == 'compute.regionDisks':
      service = client.regionDisks
      request_type = messages.ComputeRegionDisksGetRequest
    else:
      raise ValueError('Unexpected resource argument of {}'
                       .format(disk_ref.Collection()))

    disk = service.Get(request_type(**disk_ref.AsDict()))

    if args.all:
      # removing all existing labels from the disk.
      remove_labels = {}
      if disk.labels:
        for label in disk.labels.additionalProperties:
          remove_labels[label.key] = label.value

    if disk_ref.Collection() == 'compute.disks':
      replacement = labels_util.UpdateLabels(
          disk.labels,
          messages.ZoneSetLabelsRequest.LabelsValue,
          remove_labels=remove_labels)
      request = messages.ComputeDisksSetLabelsRequest(
          project=disk_ref.project,
          resource=disk_ref.disk,
          zone=disk_ref.zone,
          zoneSetLabelsRequest=messages.ZoneSetLabelsRequest(
              labelFingerprint=disk.labelFingerprint,
              labels=replacement))
    else:
      replacement = labels_util.UpdateLabels(
          disk.labels,
          messages.RegionSetLabelsRequest.LabelsValue,
          remove_labels=remove_labels)
      request = messages.ComputeRegionDisksSetLabelsRequest(
          project=disk_ref.project,
          resource=disk_ref.disk,
          region=disk_ref.region,
          regionSetLabelsRequest=messages.RegionSetLabelsRequest(
              labelFingerprint=disk.labelFingerprint,
              labels=replacement))

    if not replacement:
      return disk

    return service.SetLabels(request)
