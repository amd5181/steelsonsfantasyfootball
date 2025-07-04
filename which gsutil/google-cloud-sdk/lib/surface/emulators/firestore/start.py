# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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
"""gcloud datastore emulator start command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import socket
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.emulators import firestore_util
from googlecloudsdk.command_lib.emulators import util
from googlecloudsdk.command_lib.util import java
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Start(base.Command):
  """Start a local Firestore emulator.

  This command starts a local Firestore emulator.
  """

  detailed_help = {
      'EXAMPLES':
          """\
          To start the local Firestore emulator, run:

            $ {command}

          To bind to a specific host and port, run:

            $ {command} --host-port=0.0.0.0:8080

          To run the local Firestore emulator with a Firebase Rules set, run:

            $ {command} --rules=firestore.rules

          To run the local Firestore emulator in Datastore Mode, run:

            $ {command} --database-mode=datastore-mode

          To import data at the start of the Firestore emulator, run:

            $ {command} --import-data=<path/to/file>

          To export emulator data upon emulator shutdown, run:

            $ {command} --export-on-exit=<path/to/directory>
          """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--rules',
        required=False,
        help='If set, all projects will use the security rules in this file. '
        'More information on Firebase Rules and the syntax for this file '
        'is available at https://firebase.google.com/docs/rules.')
    parser.add_argument(
        '--host-port',
        required=False,
        type=lambda arg: arg_parsers.HostPort.Parse(arg, ipv6_enabled=True),
        help='The host:port to which the emulator should be bound. Can '
        'take the form of a single address (hostname, IPv4, or IPv6) and/or '
        'port:\n\n  [ADDRESS][:PORT]\n\n'
        'In this format you must enclose IPv6 addresses in square brackets: '
        'e.g.\n\n'
        '  [2001:db8:0:0:0:ff00:42:8329]:8080\n\n'
        'The default value is localhost:8080.')
    parser.add_argument(
        '--database-mode',
        required=False,
        help='The database mode to start the Firestore Emulator in. The valid '
        'options are: \n\n'
        '  `firestore-native` (default): start the emulator in Firestore '
        'Native\n'
        '  `datastore-mode`: start the emulator in Datastore Mode')
    parser.add_argument(
        '--use-firestore-in-datastore-mode',
        default=False,
        action='store_true',
        hidden=True,
        help='Runs the emulator in Datastore Mode.')
    parser.add_argument(
        '--import-data',
        required=False,
        help='File path to the data to be loaded into the emulator upon start '
        'up. Example:`/home/user/myexports/sampleExport/sampleExport.overall_export_metadata.`')
    parser.add_argument(
        '--export-on-exit',
        required=False,
        help='Directory path in which emulator data will be saved upon '
        'shutdown. Example:`/home/user/myexports/2024-03-26/`')
    parser.add_argument(
        '--licenses',
        default=False,
        action='store_true',
        help='If set, the emulator will print open-source dependencies and '
        'licenses, then exit.')

  # TODO(b/354923511): Remove this warning after b/354923511 is fixed.
  def LogJavaVersionWarning(self):
    """Log a warning message notifying users about Java version change.

    Log the warning when the installed JRE has an earlier version than Java 21.
    """
    try:
      java.RequireJavaInstalled(firestore_util.FIRESTORE_TITLE, min_version=21)
    except java.JavaVersionError:
      log.warning(
          'Cloud Firestore Emulator support for Java JRE version 11 will be '
          'dropped after gcloud command-line tool release 528.0.0. Please '
          'upgrade to Java JRE version 21 or higher to continue using the '
          'latest Cloud Firestore Emulator.')
    except java.JavaError:
      # A JRE could not be found. Not logging the warning since the user will
      # not be able to start an emulator anyways.
      pass

  def Run(self, args):
    if not args.host_port:
      args.host_port = arg_parsers.HostPort.Parse(
          firestore_util.GetHostPort(), ipv6_enabled=socket.has_ipv6)
    args.host_port.host = args.host_port.host or 'localhost'
    args.host_port.port = args.host_port.port or '8080'
    args.database_mode = args.database_mode or 'firestore-native'
    firestore_util.ValidateStartArgs(args)
    self.LogJavaVersionWarning()
    java.RequireJavaInstalled(firestore_util.FIRESTORE_TITLE, min_version=11)
    with firestore_util.StartFirestoreEmulator(args) as proc:
      util.PrefixOutput(proc, 'firestore')
