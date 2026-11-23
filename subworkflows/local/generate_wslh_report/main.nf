//
// Subworkflow for WSLH report generation
//

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { VADR                                         } from '../../../modules/local/vadr/main'
include { NEXTCLADE_DB_INFO as NEXTCLADE_DB_INFO_N450  } from '../../../modules/nf-core/bedtools/coverage/main'
include { NEXTCLADE_DB_INFO as NEXTCLADE_DB_INFO_WGS   } from '../../../modules/nf-core/bedtools/coverage/main'
//include { MOSDEPTH_GENOME_REGIONS                      } from '../../../modules/local/custom/amplicon_depth_heatmap/main'
//include { WSLH_REPORT                                  } from '../../../modules/local/custom/sample_amplicon_depth/main'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SUBWORKFLOW TO GENERATE REPORTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow GENERATE_WSLH_REPORT {

    take:
    ch_consensus          // channel: [ val(meta), path(fasta) ]                        consensus sequences
    //ch_bam_bai_bed    // channel: [ val(meta), path(bam), path(bai), path(bed) ]    bam files
    //ch_n450_dataset   // channel: path(dataset_dir_n450)                                 Nextclade N450 dataset
    //ch_wgs_dataset    // channel: path(dataset_dir)                                 Nextclade WGS dataset

    main:

    ch_versions = Channel.empty()


    if (!skip_vadr) {

    // Prepare ch_consensus for vadr
        ch_consensus.view()
        ch_vadr_input = ch_consensus
            .map { meta, fasta -> fasta }
            .collect().view()
    //
    // MODULE: VADR
    //
        VADR ( ch_vadr_input )
        ch_versions = ch_versions.mix(VADR.out.versions.first())
    }

    //
    // MODULE: Summarise coverage per genome region with Mosdepth
    // TODO: solve way to get depth of each reion at specific depth
    //

    //
    // MODULE: Nextclade dataset info
    // TODO: Python script to grab info from pathogen.json for each nextclade dataset
    //

    //
    // Join sample reports together and merge on meta; moddule or nextflow script
    //

    //
    // MODULE: WSLH report
    //
    

    emit:
    //report   = WSLH_REPORT.out.report   // channel: [ val(meta), path(report) ]
    versions = ch_versions              // channel: path(versions.yml)
}