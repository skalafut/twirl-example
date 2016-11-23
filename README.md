
![AlphaTwirl](images/AlphaTwirl.png?raw=true)

---

A Python library for summarizing event data in ROOT Trees

#### Description
The library contains a set of Python classes which can be used to loop over event data, summarize them, and store the results for further analysis or visualization. Event data here are defined as any data with one row (or entry) for one event; for example, data in [ROOT](https://root.cern.ch/) [TTrees](https://root.cern.ch/doc/master/classTTree.html) are event data when they have one entry for one proton-proton collision event. Outputs of this library are typically not event data but multi-dimensional categorical data, which have one row for one category. Therefore, the outputs can be imported into [R](https://www.r-project.org/) or [pandas](http://pandas.pydata.org/) as data frames. Then, users can continue a multi-dimensional categorical analysis with R, pandas, and other modern data analysis tools.

#### Example Instructions
checkout CMSSW_8_0_20_patch1, cd to the src directory, execute cmsenv, and make a directory named AlphaTwirl.  cd to AlphaTwirl, then checkout the branch v0.9.x of TaiSakuma/AlphaTwirl. Make a grid certificate proxy, and update your PYTHONPATH variable to include the current directory:

	export PYTHONPATH=$PWD:$PYTHONPATH

Now checkout the example.  go up one directory and make a directory named twirlExample.  cd to twirlExample, then checkout the current master branch of twirl-example in the current directory.  This will give you a copy of this README.md file, Framework.py, Scribbler.py (empty by default), and twirl.py. Framework.py builds the structure needed to run AlphaTwirl in a generic way, and twirl.py defines the particular attributes of an AlphaTwirl job - what variables to analyze and the binning used for each variable, references to the input .root files and output file directory name, and other job specific parameters which are specified on the command line at execution. By default twirl.py is configured to study the number of jets, HT, MHT, and jet pt by parsing a tree which contains branches named mht40_pt, ht40, nJet40, and jet_pt. Run the example by executing this command one directory above the twirlExample directory:

	./twirlExample/twirl.py --input-files /afs/cern.ch/work/s/sakuma/public/cms/c150130_RA1_data/80X/MC/20160811_B01/ROC_MC_SM/TTJets_HT600to800_madgraphMLM/roctree/tree.root --dataset-names TTJets_HT600to800 -o testTbl -n 50000

50000 events from tree.root will be processed, and the output files will be stored in a directory named testTbl. In twirl.py, six dictionaries are defined in tblcfg, each linked to one or more branch names in the tree stored in tree.root. Correspondingly, in the testTbl directory there are six txt files. Now open the file tbl_n_component.ht.txt.

The --dataset-names specified on the command line when twirl.py was run appear in each output txt file as the component name. Here only one dataset is analyzed, TTJets_HT600to800. In any collision event there is only one value of HT, and the distribution of HT across 50000 events is summarized in this txt file. The value in the ht column indicates the lower bin edge in HT, and the minimum bin width (set in twirl.py) is 10 GeV. The smallest HT value found in any event is between 480 and 490, thus the first bin covers HT from 480 to 490 GeV. The second row in this txt file indicates that there are 2 events, both with weight 1, which have HT between 480 and 490 GeV. The third row indicates there are 0 events which have HT between 490 and 510 GeV (if two consecutive bins have no entries they are combined in one row in the output file). In total, there are 1167 events with HT between 480 and 800 GeV.

Now open the file tbl_n_component.ht.jet_pt-w.txt. Here the distribution of events in HT and jet pt is summarized in two large bins of HT, and smaller log scaled bins in jet pt. As found earlier, the lowest HT in any event out of the 50000 events analyzed is between 480 and 490 GeV. In this new txt file, a much coarser binning is used in HT - from 400 to 800 GeV, and above 800 GeV (bins below 400 GeV are defined in twirl.py, but they are not relevant for this set of events). In the 1167 event subset which have HT between 400 and 800 GeV, there are 767 jets with pt between 39.8 and 50.1 GeV. Furthermore, there are 787 jets which have pt between 50.1 and 63.09 GeV.

#### Under the hood of twirl.py
The file twirl.py contains comments to explain what should be modified to tailor AlphaTwirl to different applications. Scribblers are used to calculate new quantities using multiple branches defined in the input TTree. The binning for different variables can be adjusted by hand in tblcfg, or defined as an instance of the Binning class. tblcfg defines precisely what is done for each event processed by AlphaTwirl. Each dictionary entry in tblcfg must be initialized with a list of keyAttrNames, binnings, and keyOutColumnNames. The keyAttrNames list should contain branch names which exist in the TTree in the input root file. Binnings is a list which contains binning defined by hand or defined earlier as objects of the Binning class, and keyOutColumnNames is a list with the names of the variable columns in the output txt file tied to the dictionary. If a branch is specified in keyAttrNames which can have more than one entry per event, like jet pt or lepton eta, then an additional list argument named keyIndices must be specified. Take the last dictionary defined in tblcfg as an example. It summarizes events in terms of HT and jet pt. keyIndices is a 2 element list, whose first element is None. This indicates that there is only one HT value per event. The second list element is an asterisk without enclosing parentheses. This asterisk indicates that all jets in each event should be considered, and their indices do not need to be tracked as they will not be used further. If jet pt and eta were being studied, then the asterisk around the keyIndices element tied to jet pt could be enclosed in paretheses, and the 3rd element in keyIndices, corresponding to jet eta, could be '\\1'.

#### Example Modifications
Imagine you had a tree, like the one used in the example, which contained gen jet pt, eta, phi, and mass, and you want to study the total gen jet mass in each event as a function of gen jet pt eta and phi.  This can be done by implementing a Sum dict in tblcfg of twirl.py, like this:

        dict(
            keyAttrNames = ('genJet_eta', 'genJet_pt', 'genJet_phi'),
            keyIndices = ('(*)', '\\1', '\\1'),
            binnings = (Binning(boundaries = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)), htbin, Binning(boundaries = (-4, -3, -2, -1, 0, 1, 2, 3, 4)) ),
            valAttrNames = ('genJet_mass', ),
            valIndices = ('\\1', ),
            keyOutColumnNames = ('genJetEta', 'genJetPt', 'genJetPhi'),
            valOutColumnNames = ('genJetMass', ),
            summaryClass = AlphaTwirl.Summary.Sum,
        ),


