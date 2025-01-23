from unittest.mock import Mock

from cc2olx.olx_generators import VideoOlxGenerator


class TestVideoOlxGenerator:
    def test_nodes_creation(self):
        generator = VideoOlxGenerator(Mock())
        expected_video_xml = '<video youtube="1.00:ABCDeF12345" youtube_id_1_0="ABCDeF12345"/>'

        nodes = generator.create_nodes({"youtube": "ABCDeF12345"})

        assert len(nodes) == 1
        assert nodes[0].toxml() == expected_video_xml
