import netaddr
from django.test import TestCase

from dcim.models import Device, Interface
from ipam.models import VRF
from utilities.testing import create_test_device

from netbox_routing.filtersets import *
from netbox_routing.models import *



class StaticRouteTestCase(TestCase):
    queryset = StaticRoute.objects.all()
    filterset = StaticRouteFilterSet

    @classmethod
    def setUpTestData(cls):
        devices = [create_test_device(name='Device 1'), create_test_device(name='Device 2')]
        vrf = VRF.objects.create(name='Test VRF')

        nh = netaddr.IPAddress('10.10.10.1')

        routes = (
            StaticRoute(name="Route 1", vrf=vrf, prefix='0.0.0.0/0', next_hop=nh),
            StaticRoute(name="Route 2", vrf=vrf, prefix='1.1.1.0/24', next_hop=netaddr.IPAddress('10.10.10.2')),
            StaticRoute(name="Route 3", prefix='0.0.0.0/0', next_hop=nh, metric=100)
        )

        StaticRoute.objects.bulk_create(routes)

        routes[0].devices.set([devices[0]])
        routes[1].devices.set([devices[0]])
        routes[2].devices.set([devices[1]])

    def test_q(self):
        params = {'q': 'Route 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Route 1', 'Route 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        params = {'device': ['Device 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vrf(self):
        params = {'vrf': ['Test VRF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_prefix(self):
        params = {'prefix': '0.0.0.0/0'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_next_hop(self):
        params = {'next_hop': '10.10.10.1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_metric(self):
        params = {'metric': [1]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)



class OSPFInstanceTestCase(TestCase):
    queryset = OSPFInstance.objects.all()
    filterset = OSPFInstanceFilterSet

    @classmethod
    def setUpTestData(cls):
        devices = [
            create_test_device(name='Device 1'),
            create_test_device(name='Device 2'),
            create_test_device(name='Device 3'),
            create_test_device(name='Device 4'),
        ]

        data = (
            OSPFInstance(name='Instance 1', device=devices[0], router_id='0.0.0.0', process_id=0),
            OSPFInstance(name='Instance 2', device=devices[1], router_id='1.1.1.1', process_id=1),
            OSPFInstance(name='Instance 3', device=devices[2], router_id='2.2.2.2', process_id=2),
            OSPFInstance(name='Instance 3', device=devices[3], router_id='3.3.3.3', process_id=3),
        )

        OSPFInstance.objects.bulk_create(data)

    def test_q(self):
        params = {'q': 'Instance 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Instance 1', 'Instance 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        data = Device.objects.all()[0:2]

        params = {'device_id': [data[0].pk, data[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {'device': [data[0].name, data[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_process_id(self):
        params = {'process_id': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_router_id(self):
        params = {'router_id': ['1.1.1.1', '2.2.2.2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)



class OSPFAreaTestCase(TestCase):
    queryset = OSPFArea.objects.all()
    filterset = OSPFAreaFilterSet

    @classmethod
    def setUpTestData(cls):

        data = (
            OSPFArea(area_id='0.0.0.0'),
            OSPFArea(area_id='1.1.1.1'),
            OSPFArea(area_id=0),
            OSPFArea(area_id=1),
        )

        OSPFArea.objects.bulk_create(data)

    def test_q(self):
        params = {'q': '1.1.1.1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_area_id(self):
        params = {'area_id': ['0', '1.1.1.1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class OSPFInterfaceTestCase(TestCase):
    queryset = OSPFInterface.objects.all()
    filterset = OSPFInterfaceFilterSet

    @classmethod
    def setUpTestData(cls):
        devices = (
            create_test_device(name='Device 1'),
            create_test_device(name='Device 2'),
            create_test_device(name='Device 3'),
            create_test_device(name='Device 4'),
        )
        interfaces = (
            Interface(device=devices[0], name='Interface 1', type='virtual'),
            Interface(device=devices[1], name='Interface 2', type='virtual'),
            Interface(device=devices[2], name='Interface 3', type='virtual'),
            Interface(device=devices[3], name='Interface 4', type='virtual'),
        )
        Interface.objects.bulk_create(interfaces)

        areas = (
            OSPFArea(area_id='0.0.0.0'),
            OSPFArea(area_id=1),
            OSPFArea(area_id='2.2.2.2'),
            OSPFArea(area_id=3),
        )
        OSPFArea.objects.bulk_create(areas)

        instances = (
            OSPFInstance(name='Instance 0', device=devices[0], router_id='0.0.0.0', process_id=0),
            OSPFInstance(name='Instance 1', device=devices[1], router_id='1.1.1.1', process_id=1),
            OSPFInstance(name='Instance 2', device=devices[2], router_id='2.2.2.2', process_id=2),
            OSPFInstance(name='Instance 3', device=devices[3], router_id='3.3.3.3', process_id=3),
        )
        OSPFInstance.objects.bulk_create(instances)

        data = (
            OSPFInterface(interface=interfaces[0], instance=instances[0], area=areas[0]),
            OSPFInterface(interface=interfaces[1], instance=instances[1], area=areas[1]),
            OSPFInterface(interface=interfaces[2], instance=instances[2], area=areas[2]),
            OSPFInterface(interface=interfaces[3], instance=instances[3], area=areas[3]),
        )
        OSPFInterface.objects.bulk_create(data)

    def test_q(self):
        params = {'q': 'Interface 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {'q': 'Instance 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_instances(self):
        data = OSPFInstance.objects.all()[0:2]

        params = {'instance_id': [data[0].pk, data[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {'instance': [data[0].name, data[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_area(self):
        data = OSPFArea.objects.all()[0:2]

        params = {'area_id': [data[0].pk, data[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {'area': [data[0].area_id, data[1].area_id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devices(self):
        data = Device.objects.all()[0:2]

        params = {'device_id': [data[0].pk, data[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {'device': [data[0].name, data[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_interfaces(self):
        data = Interface.objects.all()[0:2]

        params = {'interface_id': [data[0].pk, data[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {'interface': [data[0].name, data[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
