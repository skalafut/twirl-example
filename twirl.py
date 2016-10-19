#!/usr/bin/env python
# Tai Sakuma <sakuma@cern.ch>
import os, sys
import argparse

##__________________________________________________________________||
parser = argparse.ArgumentParser()
parser.add_argument("--input-files", default = [ ], nargs = '*', help = "list of input files")
parser.add_argument("--dataset-names", default = [ ], nargs = '*', help = "list of data set names")
parser.add_argument("-p", "--process", default = 1, type = int, help = "number of processes to run in parallel")
parser.add_argument('-o', '--outdir', default = os.path.join('tbl', 'out'))
parser.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'quiet mode')
parser.add_argument('-n', '--nevents', default = -1, type = int, help = 'maximum number of events to process for each component')
parser.add_argument('--max-events-per-process', default = -1, type = int, help = 'maximum number of events per process')
parser.add_argument('--force', action = 'store_true', default = False, help = 'recreate all output files')
args = parser.parse_args()

##__________________________________________________________________||
import AlphaTwirl
import Framework
import Scribbler

##__________________________________________________________________||
def main():

    reader_collector_pairs = [ ]

    #
    # configure scribblers
    #
    NullCollector = AlphaTwirl.Loop.NullCollector
    reader_collector_pairs.extend([
        ])

    #
    # configure tables
    #
    Binning = AlphaTwirl.Binning.Binning
    Echo = AlphaTwirl.Binning.Echo
    Round = AlphaTwirl.Binning.Round
    RoundLog = AlphaTwirl.Binning.RoundLog
    Combine = AlphaTwirl.Binning.Combine
    echo = Echo(nextFunc = None)
    echoNextPlusOne = Echo()
    htbin = Binning(boundaries = (0, 200, 400, 800))
    njetbin = Binning(boundaries = (1, 2, 3, 4, 5))
    tblcfg = [
        dict(keyAttrNames = ('mht40_pt', ), binnings = (Round(10, 0), ), keyOutColumnNames = ('mht', )),
        dict(keyAttrNames = ('ht40', 'mht40_pt'), binnings = (htbin, Round(10, 0)), keyOutColumnNames = ('ht', 'mht')),
        dict(keyAttrNames = ('ht40', 'nJet40', 'mht40_pt'), binnings = (htbin, njetbin, Round(10, 0)), keyOutColumnNames = ('ht', 'njet', 'mht')),
        dict(keyAttrNames = ('ht40', 'jet_pt'), binnings = (htbin, RoundLog(0.1, 100)), keyIndices = (None, 0), keyOutColumnNames = ('ht', 'jet_pt')),
        dict(keyAttrNames = ('ht40', 'jet_pt'), binnings = (htbin, RoundLog(0.1, 100)), keyIndices = (None, '*'), keyOutColumnNames = ('ht', 'jet_pt')),
        ]

    # complete table configs
    tableConfigCompleter = AlphaTwirl.Configure.TableConfigCompleter(
        defaultSummaryClass = AlphaTwirl.Summary.Count,
        defaultOutDir = args.outdir,
        createOutFileName = AlphaTwirl.Configure.TableFileNameComposer2()
    )
    tblcfg = [tableConfigCompleter.complete(c) for c in tblcfg]

    # do not recreate tables that already exist unless the force option is used
    if not args.force:
        tblcfg = [c for c in tblcfg if c['outFile'] and not os.path.exists(c['outFilePath'])]

    reader_collector_pairs.extend(
        [AlphaTwirl.Configure.build_counter_collector_pair(c) for c in tblcfg]
    )

    #
    # configure data sets
    #
    dataset_names = args.dataset_names if args.dataset_names else args.input_files
    datasets = [Framework.Dataset(n, f) for n, f in zip(dataset_names, args.input_files)]

    #
    # run
    #
    fw =  Framework.Framework(
        quiet = args.quiet,
        process = args.process,
        max_events_per_dataset = args.nevents,
        max_events_per_process = args.max_events_per_process
    )
    fw.run(
        datasets = datasets,
        reader_collector_pairs = reader_collector_pairs
    )

##__________________________________________________________________||
def greater_than_zero(x): return x > 0

##__________________________________________________________________||
if __name__ == '__main__':
    main()
