import logging
import requests

from song.original_song_cli.entities import Study, Donor, Specimen, Sample, File, SequencingRead

from song.original_song_cli.tools import SimplePayloadBuilder
from song.original_song_cli.client import Api, StudyClient, ManifestClient
from song.original_song_cli.model import ApiConfig

def _get_logger():
    return logging.getLogger(__name__)

class SongClient(object):
    schemas_url = '{base_url}/schemas'
    studies_list_url = '{base_url}/studies/all'
    submit_url = '{base_url}/submit/{studyId}'

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
        logger = _get_logger()
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
        logger = _get_logger()
        logger.debug("Analysis creation payload: {payload}".format(payload=payload))
        res = requests.post(
            self.submit_url.format(base_url=self.base_url, studyId=study_id), 
            data=payload,
            verify=False,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token),
                'Content-Type': 'application/json'
            }
        )
        logger.debug('upload status code: {code}'.format(code=res.status_code))
        logger.debug('upload response: {response}'.format(response=res.content))
        assert res.status_code == 200
        return res.json()

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
        logger = _get_logger()
        logger.debug("Schema creation payload: {payload}".format(payload=schema))
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
    
    def get_studies_list(self):
        res = requests.get(
            self.studies_list_url.format(base_url=self.base_url), 
            verify=False,
            headers={
                'Authorization': 'Bearer {token}'.format(token=self.token)
            }
        )
        assert res.status_code == 200
        return res.json()
