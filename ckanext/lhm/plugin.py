import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from ckan.plugins.interfaces import IConfigurer, IDatasetForm
from ckan.lib.plugins import DefaultTranslation
import ckanext.lhm.cli as cli

# import ckanext.lhm.cli as cli
import ckanext.lhm.helpers as helpers
# import ckanext.lhm.views as views
from ckanext.lhm.logic import action
#     (action, auth, validators
# )


#from ckanext.datastore.backend.postgres import _cache_types
from sqlalchemy import create_engine

# This function extends the data types in postgresql.
# This is required for Data Dictionary and is an extension to the function _cache_types in Datastor.backend.postgres.py
def _data_dict_type():
    eng = toolkit.config['ckan.datastore.write_url']
    _pg_types = {}
    _type_names = set()
    engine = create_engine(eng)
    connection = engine.connect()
    if not _pg_types:
        results = connection.execute(
            'SELECT oid, typname FROM pg_type;'
        )
        for result in results:
            _pg_types[result[0]] = result[1]
            _type_names.add(result[1])

    if 'number_' not in _type_names:
        with engine.begin() as write_connection:
            write_connection.execute(
                'CREATE TYPE "number_" AS (number text)')
            # Add 'number' to _pg_types dictionary with a custom OID
            _pg_types[9000] = 'number_'  # You can use any unique OID here
            _type_names.add('number_')
    if 'sdo_geometry' not in _type_names:
        with engine.begin() as write_connection:
            write_connection.execute(
                'CREATE TYPE "sdo_geometry" AS (sdo_geometry text)')
            # Add 'sdo_geometry' to _pg_types dictionary with a custom OID
            _pg_types[6001] = 'sdo_geometry'  # You can use any unique OID here
            _type_names.add('sdo_geometry')
    if 'nvarchar2' not in _type_names:
        with engine.begin() as write_connection:
            write_connection.execute(
                'CREATE TYPE "nvarchar2" AS (nvarchar2 text)')
            # Add 'nvarchar2' to _pg_types dictionary with a custom OID
            _pg_types[6002] = 'nvarchar2'  # You can use any unique OID here
            _type_names.add('nvarchar2')
    # if 'float' not in _type_names:
    #     with engine.begin() as write_connection:
    #         write_connection.execute(
    #             'CREATE TYPE "float" AS (float text)')
    #         # Add 'float' to _pg_types dictionary with a custom OID
    #         _pg_types[6003] = 'float'  # You can use any unique OID here
    #         _type_names.add('float')
    if 'blob' not in _type_names:
        with engine.begin() as write_connection:
            write_connection.execute(
                'CREATE TYPE "blob" AS (blob text)')
            # Add 'blob' to _pg_types dictionary with a custom OID
            _pg_types[6004] = 'blob'  # You can use any unique OID here
            _type_names.add('blob')
_data_dict_type()

class LHMCatalogPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer, inherit=True)
    # p.implements(p.IDatasetForm, inherit=True)
    # p.implements(p.IAuthFunctions)
    # p.implements(p.IActions)
    # p.implements(p.IBlueprint)
    p.implements(p.IClick)
    p.implements(p.ITranslation, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    # p.implements(p.IValidators)
    
    
    def i18n_domain(self):
        return 'ckanext-lhm'

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource("assets", "ckanext-lhm")


        config['scheming.presets'] = """
        ckanext.scheming:presets.json
        ckanext.composite:presets.json
        ckanext.lhm:schemas/presets.yaml
        """ + (
                "ckanext.validation:presets.json" if "validation" in config['ckan.plugins'] else
                "ckanext.lhm:schemas/validation_placeholder_presets.yaml"
        )

        # config['scheming.dataset_schemas'] = """
        # ckanext.lhm:schemas/lhm_dataset.yaml
        # """

    # ITemplateHelpers

    def get_helpers(self):
        return dict(helpers.all_helpers)
        # retunr dict((h, getattr(helpers, h)) for h in [
        #     'user_info',#: helpers.user_info
        # ])


    def before_dataset_index(self, data_dict):      
        return self.before_index(data_dict)

    def before_index(self, data_dict):

        usage_keywords = []
        usage_remarks = []
        #changed_date = []
        for sub in data_dict.get('additional_usage_notes', []):
            usage_keywords.append(sub['usage_keywords'])
            usage_remarks.append(sub['usage_remarks'])
            #changed_date.append(sub['changed_date'])

        # replace list of dicts with plain texts to prevent Solr errors
        data_dict['additional_usage_notes'] = '\n'.join(usage_keywords)
        data_dict['additional_usage_notes'] = '\n'.join(usage_remarks)
        #data_dict['change_history'] = '\n'.join(changed_date)

        ###### For Attribute Change Documentation
        change = []
        editor = []
        #changed_date = []
        for sub in data_dict.get('change_history', []):
            change.append(sub['change'])
            editor.append(sub['editor'])
            #changed_date.append(sub['changed_date'])

        # replace list of dicts with plain texts to prevent Solr errors
        data_dict['change_history'] = '\n'.join(change)
        data_dict['change_history'] = '\n'.join(editor)
        #data_dict['change_history'] = '\n'.join(changed_date)

        return data_dict

    def is_fallback(self):
        return False

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

    # IClick

    def get_commands(self):
        return cli.get_commands() 

    # IAuthFunctions

    # def get_auth_functions(self):
    #     return auth.get_auth_functions()

    # IValidators

    # def get_validators(self):
    #     return validators.get_validators()

    

    # def form_to_db_schema(self):
    #     schema = SchemingDatasets.form_to_db_schema()
    #     # Merge your new schema with the existing schema
    #     schema.update({
    #         'my_schema': {'some_field': ['ckanext.scheming:field_text']}
    #     })
    #     return schema


class LHMThemePlugin(p.SingletonPlugin, DefaultTranslation):
    '''Theme plugin for LHM UDP Catalog.'''

    # Declare the iterfaces this class implements
    #p.implements(p.IBlueprint)
    p.implements(p.IConfigurer)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IActions)
    #p.implements(p.ITemplateHelpers)

    if toolkit.check_ckan_version("2.9"):
        # IConfigurer
        def update_config(self, config):
            p.toolkit.add_template_directory(config, 'theme_templates_2.9.9')
            p.toolkit.add_public_directory(config, 'public')
            p.toolkit.add_resource('assets_theme_2.9.9', 'lhm_theme')

    elif toolkit.check_ckan_version("2.10"):
        # IConfigurer
        def update_config(self, config):
            p.toolkit.add_template_directory(config, 'theme_templates')
            p.toolkit.add_public_directory(config, 'public')
            p.toolkit.add_resource('assets_theme', 'lhm_theme')


    # IActions
    def get_actions(self):
        return {
            'user_create': action.user_create,
        }
