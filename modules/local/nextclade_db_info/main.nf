process NEXTCLADE_DB_INFO {
    tag "$dataset.name"
    label 'process_single'
    
    //conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9--1' :
        'biocontainers/python:3.9--1' }"

    input:
    path dataset // a downloaded Nextclade dataset directory containing pathogen.json

    output:
    //path "*.csv", emit: info
    //path "versions.yml", emit: versions

    script:
    def prefix = task.ext.prefix ?: "${dataset.name}"
    """
    ls -l ${dataset}/pathogen.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        nextclade_dataset_name: "version_of_dataset"
    END_VERSIONS
    """
}