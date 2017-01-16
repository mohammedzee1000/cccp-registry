# Important more generic pattern should be lower than more specific pattern
from collections import OrderedDict
config = {
    "index_git": "https://github.com/centos/container-index",
    "index_git_clone": "./c_i",
    "dump_location": "./dump_file",
    "registry": "registry.centos.org",
    "section_mappings": OrderedDict([
        ("predef_origin", {
            "title": "Openshift Origin Containers",
            "pattern": [
                "^openshift/.*$"
            ]
        }),
        ("predef_centos_base", {
            "title": "CentOS Base Containers",
            "pattern": [
                "^centos/centos.*$"
            ]
        }),
        ("predefcentos_dockerfiles", {
            "title": "CentOS Containers",
            "pattern": [
                "^centos/.*$"
            ]
        }),
        ("predef_sclo", {
            "title": "Software Collections Containers",
            "pattern": [
                "^sclo/.*$"
            ]
        }),
        ("predef_gluster", {
            "title": "Gluster Containers",
            "pattern": [
                "^gluster/.*$"
            ]
        }),
        ("predef_mattermost", {
            "title": "Mattermost Containers",
            "pattern": [
                "^.*/mattermost*$",
                "^sgk/.*$"
            ]
        }),
        ("predef_postgresql", {
            "title": "Postgresql Container",
            "pattern": [
                "^mohammedzee1000/postgresql.*$"
            ]
        }),
        ("predef_jboss", {
            "title": "JBoss Containers",
            "pattern": [
                "^jboss/.*$",
                "^mohammedzee1000/keycloak-postgres:latest$"
            ]
        }),
        ("predef_eclipse", {
            "title": "Eclipse Che Containers",
            "pattern": [
                "^eclipse/.*$"
            ]
        }),
        ("predef_cockpit", {
            "title": "Cockpit Containers",
            "pattern": [
                "^cockpit/.*$"
            ]
        }),
        ("predef_project_atomic", {
            "title": "Project Atomic Containers",
            "pattern": [
                "^projectatomic/.*$"
            ]
        })
    ])
}

