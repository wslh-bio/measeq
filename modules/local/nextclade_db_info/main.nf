process NEXTCLADE_DB_INFO {
    tag "$dataset.name"
    label 'process_single'
    
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9--1' :
        'biocontainers/python:3.9--1' }"

    input:
    path dataset

    output:
    path "*.tsv",           emit: info
    path "versions.yml",    emit: versions

    script:
    def args = task.ext.args ?: ''
    """
    nextclade_db_info.py \\
        --db_dir ${dataset} \\
        ${args}

    DB_NAME=\$(awk -F'\\t' 'NR==2 {print \$2}' *_db_info.tsv)
    DB_VERSION=\$(awk -F'\\t' 'NR==2 {print \$3}' *_db_info.tsv)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python3 --version | sed 's/Python //g')
        "\${DB_NAME}": "\${DB_VERSION}"
    END_VERSIONS
    """

    stub:
    """
    touch ${dataset.baseName}_db_info.tsv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python3 --version | sed 's/Python //g')
        "${dataset.baseName}": "stub_version"
    END_VERSIONS
    """
}