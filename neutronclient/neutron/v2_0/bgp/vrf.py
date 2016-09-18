# Copyright (c) 2016 IBM.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronv20

# To understand how neutronclient extensions work
# read neutronclient/v2.0/client.py (extend_* methods and _register_extension)


def add_common_args(parser):
    """Adds to parser arguments common to create and update commands."""
    parser.add_argument(
        '--name',
        help=_('Name of the BGP VRF.'))
    parser.add_argument(
        '--import-targets',
        help=_('List of additional Route Targets to import from.'
               ' Usage: -- --import-targets list=true '
               '<asn1>:<nn1> <asn2>:<nn2> ...'))
    parser.add_argument(
        '--export-targets',
        help=_('List of additional Route Targets to export to. Usage: -- '
               '--export-targets list=true <asn1>:<nn1> <asn2>:<nn2> ...'))
    parser.add_argument(
        '--route-distinguishers',
        help=_('List of RDs that will be used to advertize VRF routes.'
               'Usage: -- --route-distinguishers list=true '
               '<asn1>:<nn1> <asn2>:<nn2> ...'))
    parser.add_argument(
        '--segmentation-id',
        help=_('Tunnel ID for VXLAN network of the gateway upstream.'))


def args2body_common_args(body, parsed_args):
    neutronv20.update_dict(parsed_args, body,
                           ['name', 'tenant_id',
                            'import_targets', 'export_targets',
                            'route_distinguishers', 'segmentation_id'])


class CreateVRF(neutronv20.CreateCommand):
    """Create a VRF."""
    resource = 'vrf'

    def add_known_arguments(self, parser):
        # type is read-only, hence specific to create
        parser.add_argument(
            '--type',
            default='evpn',
            help=_('BGP VRF type selection, only support evpn '
                   'for now'))
        add_common_args(parser)

    def args2body(self, parsed_args):
        body = {}
        body['type'] = parsed_args.type
        args2body_common_args(body, parsed_args)
        return {self.resource: body}


class UpdateVRF(neutronv20.UpdateCommand):
    """Update a given VRF."""
    resource = 'vrf'

    def add_known_arguments(self, parser):
        add_common_args(parser)

    def args2body(self, parsed_args):
        body = {}
        args2body_common_args(body, parsed_args)
        return {self.resource: body}


class DeleteVRF(neutronv20.DeleteCommand):
    """Delete a given VRF."""
    resource = 'vrf'


class ListVRF(neutronv20.ListCommand):
    """List VRFs that belong to a given tenant."""
    resource = 'vrf'
    list_columns = [
        'id', 'name', 'type', 'import_targets', 'export_targets',
        'route_distinguishers', 'segmentation_id']
    pagination_support = True
    sorting_support = True


class ShowVRF(neutronv20.ShowCommand):
    """Show a given VRF."""
    resource = 'vrf'


# VRF  associations


def _get_vrf_id(client, name_or_id):
    return neutronv20.find_resourceid_by_name_or_id(
        client, 'vrf', name_or_id)


def _get_router_id(client, name_or_id):
    return neutronv20.find_resourceid_by_name_or_id(
        client, 'router', name_or_id)


# VRF Router associations


class AssociateVRFRouter(neutronv20.NeutronCommand):
    """Create a VRF-Router association."""

    def get_parser(self, prog_name):
        parser = super(AssociateVRFRouter, self).get_parser(prog_name)
        parser.add_argument(
            'vrf',
            metavar='VRF',
            help=_('ID or name of the BGP VRF.'))
        parser.add_argument(
            'router',
            metavar='ROUTER',
            help=_('ID or name of the router.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _vrf_id = _get_vrf_id(neutron_client,
                              parsed_args.vrf)
        _router_id = _get_router_id(neutron_client,
                                    parsed_args.router)
        neutron_client.add_vrf_router_association(_vrf_id,
                                                  {'router_id': _router_id})


class DisassociateVRFRouter(neutronv20.NeutronCommand):
    """Delete a given VRF-Router association."""
    def get_parser(self, prog_name):
        parser = super(DisassociateVRFRouter, self).get_parser(prog_name)
        parser.add_argument(
            'vrf',
            metavar='VRF',
            help=_('ID or name of the BGP VRF.'))
        parser.add_argument(
            'router',
            metavar='ROUTER',
            help=_('ID or name of the router.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _vrf_id = _get_vrf_id(neutron_client,
                              parsed_args.vrf)
        _router_id = _get_router_id(neutron_client,
                                    parsed_args.router)
        neutron_client.remove_vrf_router_association(_vrf_id,
                                                     {'router_id': _router_id})
