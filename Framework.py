# Tai Sakuma <sakuma@cern.ch>
import sys
import ROOT
import AlphaTwirl

ROOT.gROOT.SetBatch(1)

##__________________________________________________________________||
class Framework(object):
    def __init__(self, quiet = False, process = 8,
                 max_events_per_dataset = -1,
                 max_events_per_process = -1
    ):
        self.progressMonitor, self.communicationChannel = AlphaTwirl.Configure.build_progressMonitor_communicationChannel(quiet = quiet, processes = process)
        self.max_events_per_dataset = max_events_per_dataset
        self.max_events_per_process = max_events_per_process

    def run(self, datasets, reader_collector_pairs):
        self._begin()
        reader_top = AlphaTwirl.Loop.ReaderComposite()
        collector_top = AlphaTwirl.Loop.CollectorComposite(self.progressMonitor.createReporter())
        for r, c in reader_collector_pairs:
            reader_top.add(r)
            collector_top.add(c)
        eventLoopRunner = AlphaTwirl.Loop.MPEventLoopRunner(self.communicationChannel)
        eventBuilder = EventBuilder(maxEvents = self.max_events_per_dataset)
        eventReader = AlphaTwirl.Loop.EventReader(
            eventBuilder = eventBuilder,
            eventLoopRunner = eventLoopRunner,
            reader = reader_top,
            collector = collector_top,
            maxEventsPerRun = self.max_events_per_process
        )
        eventReader.begin()
        for dataset in datasets:
            eventReader.read(dataset)
        eventReader.end()
        self._end()

    def _begin(self):
        self.progressMonitor.begin()
        self.communicationChannel.begin()

    def _end(self):
        self.progressMonitor.end()
        self.communicationChannel.end()

##__________________________________________________________________||
class Dataset(object):
    def __init__(self, name, file_):
        self.name = name
        self.file_ = file_

##__________________________________________________________________||
class EventBuilder(object):
    def __init__(self, maxEvents = -1):
        self.maxEvents = maxEvents
        self.treeName = 'tree'

    def getNumberOfEventsInDataset(self, dataset):
        file = ROOT.TFile.Open(dataset.file_)
        tree = file.Get(self.treeName)
        return self._minimumPositiveValue([self.maxEvents, tree.GetEntries()])

    def build(self, dataset, start = 0, nEvents = -1):
        file = ROOT.TFile.Open(dataset.file_)
        tree = file.Get(self.treeName)
        maxEvents = self._minimumPositiveValue([self.maxEvents, nEvents])
        ret = AlphaTwirl.Events.BEvents(tree, maxEvents, start)
        ret.dataset = dataset.name
        return ret

    def _minimumPositiveValue(self, vals):
        vals = [v for v in vals if v >= 0]
        if not vals: return -1
        return min(vals)

##__________________________________________________________________||
