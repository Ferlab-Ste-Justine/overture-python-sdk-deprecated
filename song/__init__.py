import logging
import requests

from song.original_song_cli.entities import Study, Donor, Specimen, Sample, File, SequencingRead

from song.original_song_cli.tools import SimplePayloadBuilder
from song.original_song_cli.client import Api, StudyClient, ManifestClient
from song.original_song_cli.model import ApiConfig

logger = logging.getLogger(__name__)

class SongClient(object):
    schemas_url = '{base_url}/schemas'

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def create_study(
        self,
        id,
        name,
        description,
        organization
    ):
        api = Api(
            ApiConfig(self.base_url, id, self.token, debug=True)
        )
        study_client = StudyClient(api)
        if not study_client.has(id):
            study_client.create(
                Study.create(
                    id,
                    name,
                    description,
                    organization
                )
            )

    def create_analysis(
        self,
        study_id,
        analysis_id,
        donor,
        specimen,
        sample,
        files,
        experiment
    ):
        api = Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        )
        
        donor.studyId = study_id
        for file in files:
            file.studyId = study_id
        
        builder = SimplePayloadBuilder(donor, specimen, sample, files, experiment, study_id)
        payload = builder.to_dict()
        logger.debug("Analysis creation payload: {payload}".format(payload=payload))

        upload_response = api.upload(json_payload=payload, is_async_validation=False)
        logger.debug("upload response: {response}".format(response=upload_response))
        return upload_response

    def create_custom_analysis(
        self,
        study_id,
        payload
    ):
        api = Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        )
        logger.debug("Analysis creation payload: {payload}".format(payload=payload))
        upload_response = api.upload(json_payload=payload, is_async_validation=False)
        logger.debug("upload response: {response}".format(response=upload_response))
        return upload_response

    def get_analysis_manifest(
        self,
        study_id,
        analysis_id,
        source_dir
    ):
        return ManifestClient(
            Api(
                ApiConfig(self.base_url, study_id, self.token, debug=True)
            )
        ).create_manifest(source_dir, analysis_id)

    def publish_analysis(
        self,
        study_id,
        analysis_id
    ):
        return Api(
            ApiConfig(self.base_url, study_id, self.token, debug=True)
        ).publish(analysis_id)
    
    def get_schemas(self):
        return Api(
            ApiConfig(self.base_url, None, self.token, debug=True)
        ).list_schemas()
    
    def create_schema(self, schema):
        res = requests.post(
            self.schemas_url.format(base_url=self.base_url), 
            data=schema,
            verify=False,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token),
                'Content-Type': 'application/json'
            }
        )
        logger.debug('schema creation status code: {code}'.format(code=res.status_code))
        logger.debug('schema creation response: {response}'.format(response=res.content))
        assert res.status_code == 200