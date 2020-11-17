7#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
WORDS IN NOISE EEG EXPERIMENT
for Kelly (Turkeltaub Lab)

OSX: El Capitan (Should work on most new-ish OSX and Windows)
PsychoPy Version: 1.84.1

Written by: Kathryn Schuler (kathryn.schuler@gmail.com)
Written on: 09/29/2016
Last Updated: 11/15/2016

Expeirment version: 2.1
"""

"""
AD Updates/comments
 -- added in EEG support but need to change variable name to true
 -- right now, trigger properties still need to be defined and double checked
 -- added duplication avoidance (compares with last 20 items - ie a block) by 2 methods
    - target cannot occur within the last 20 items
    - stimulus set (alphabetized and joined) cannot occur in last 20 items
 -- staircases are now quest and not simple
 -- to support quest handler, keyword "staircase" cannot be used as a parameter in the user dictionary file
    (see data.py library in psychopy lines 2278-2282) so I renamed usages of "staircase" to "staircasename"
    in the yaml parameter file and within the script here
 -- Made it so that E and H now say Easy and Hard between each trials
 -- Order of difficulty cue
    - added a difficulty_cue_period function and made it show difficulty cue there - using parameter for the difficulty cue duraiton
    - removed cue being shown in intertrial interval period -- instead, show a gray crosshair
 -- added infinite break after baseline staircase - spacebar to progress (and short break removed after block 4 (end of baseline staircase) in parameter file.)
 -- On main staircase, intensity (this_loudness) of each trial is manually manipulated - separately for easy and hard trials.
    - trial 0 starts off with the last intensity value from the baseline block for that condition (easy, hard)
    - on the first 5 trials, the intensity is set to the same as the first trial. in other words no variation in the first 5 trials
    - then after trial 5, if average accuracy is above a desired percent, this_loudness is decreased to make the trial harder.
        - on each trial, if accuracy is below the desired percent, this_loudness is increased to make the trial easier.
-- Added verbosity switch for sox output in function mix_sound_sox() - 2/25/17

 Notes:
 -- duplicated stimuli in a given condition list need to be unique - adding a 2 or 3 to the end is fine (ie uru, uru2)
 -- the stimulus item "false" in the stimulus yaml file needs to have quotation marks around it so it is a string and not a bool
 -- with a whole-block averaging scheme for manual staircasing in main staircase -- it goes nuts and gets crazy loud or quiet
    so instead, it averages the last 5 trials to determine whether to make the stiulus louder or easier. hopefully this prevents
    the irreversible tangents of loudness (because user's correct responses add consistently less and less to the overall average)
"""


"""
*********************************************************************************
LOAD REQUIRED PACKAGES AND SET AUDIO DRIVER PREFERENCES
*********************************************************************************
"""

# import the required packages and libraries for the experiment
from psychopy import prefs, gui, core, data, visual, info, sound, event
import subprocess # to be able to access sox via subprocess.Popen() etc without popping up any windows and whatnot
import time, os, numpy, yaml, glob
import egi.simple as egi # emport egi.threaded as egi
import numpy as np, random
import math # for the db conversion in manually manipulating the staircase
from psychopy import logging
logging.console.setLevel(logging.WARNING)

# set the preferred audio driver for this machine
prefs.general['audioLib'] = ['pyo']
prefs.general['audioDriver'] = ['portaudio']

"""
*********************************************************************************
SETUP EXPERIMENT PARAMTERS
*********************************************************************************
"""

# experiment parameters are loaded into a dictionary from the params.yaml file
PARAMS = yaml.safe_load(open('params_LIPREAD.yaml', 'r'))

# get some addiitonal info about the participant via a dialogue box
# user-input parameters are set in the params.yaml file and we just
# get a timestamp for date-run
PARTICIPANT_INFO = PARAMS['experiment info']['user-input']
PARTICIPANT_INFO['date-run'] = data.getDateStr(format ='%Y-%b-%d-%H%M%S')

if not gui.DlgFromDict(PARTICIPANT_INFO, fixed = 'date', title = PARAMS['experiment info']['exp-name']).OK:
    core.quit()

"""
*********************************************************************************
 The main experiment class, which contains all the experiments objects and methods.
*********************************************************************************
"""
class WordsInNoiseEEG(object):
    def __init__(self):
        self.EXPERIMENT_DATA = data.ExperimentHandler(
            # setup the main experiment data object to keep track of all of our data
            # extra info for this could include both the EXPINFO from input and also
            # a term for {'params': PARAMS} so that it gets saved in the subject's data file
            name            = PARAMS['experiment info']['exp-name'],
            extraInfo       = PARTICIPANT_INFO,
            runtimeInfo     = info.RunTimeInfo,
            dataFileName    = PARAMS['experiment info']['data-path'] + PARTICIPANT_INFO['subject'] + '-' + PARTICIPANT_INFO['date-run']
        )
        self.EXP_WINDOW = visual.Window(
            # setup the main experiment window / screen
            screen          = PARAMS['devices']['monitor']['screen'],
            units           = PARAMS['devices']['monitor']['units'],
            color           = PARAMS['devices']['monitor']['background color'],
            fullscr         = PARAMS['devices']['monitor']['full screen']
        )
        self.INSTRUCTIONS = visual.TextStim(self.EXP_WINDOW,
            # the visual features of the main instructions for the experiment (and the rest instructions)
            text            = '',
            units           = PARAMS['stimuli']['instructions']['units'],
            pos             = PARAMS['stimuli']['instructions']['pos'],
            color           = PARAMS['stimuli']['instructions']['color'],
            height          = PARAMS['stimuli']['instructions']['height'],
            font            = PARAMS['stimuli']['instructions']['font']
        )
        self.BLOCK_TITLE = visual.TextStim(self.EXP_WINDOW,
            # the visual features of the block title
            text            = '',
            units           = PARAMS['stimuli']['block title']['units'],
            pos             = PARAMS['stimuli']['block title']['pos'],
            color           = PARAMS['stimuli']['block title']['color'],
            height          = PARAMS['stimuli']['block title']['height'],
            font            = PARAMS['stimuli']['block title']['font']
        )
        self.DIFFICULTY_TEXT = visual.TextStim(self.EXP_WINDOW,
            # the visual features of the text that appears to tell you the difficult level (H or E)
            text            = '',
            units           = PARAMS['stimuli']['difficulty text']['units'],
            pos             = PARAMS['stimuli']['difficulty text']['pos'],
            color           = PARAMS['stimuli']['difficulty text']['color'],
            height          = PARAMS['stimuli']['difficulty text']['height'],
            font            = PARAMS['stimuli']['difficulty text']['font']
        )
        self.FIXATION_CROSS = visual.TextStim(self.EXP_WINDOW,
            # the visual features of the fixation cross
            text            = '+',
            units           = PARAMS['stimuli']['fixation cross']['units'],
            pos             = PARAMS['stimuli']['fixation cross']['pos'],
            color           = PARAMS['stimuli']['fixation cross']['color'],
            height          = PARAMS['stimuli']['fixation cross']['height'],
            font            = PARAMS['stimuli']['fixation cross']['font']
        )
        self.IMAGE_MASK = visual.ImageStim(self.EXP_WINDOW,
            units             = PARAMS['stimuli']['image mask']['units'],
            pos            = PARAMS['stimuli']['image mask']['pos'],
            size            = PARAMS['stimuli']['image mask']['size'],
        )
        self.STIMULUS_SOUND = sound.Sound(value = 'Sounds/pinknoise.wav',
            sampleRate = PARAMS['stimuli']['word']['sampleRate']
        )
        self.THIS_TRIAL_SOUND = sound.Sound(value = 'Sounds/pinknoise.wav',
            sampleRate = PARAMS['stimuli']['word']['sampleRate']
        )
        self.LEFT_ANSWER = visual.TextStim(self.EXP_WINDOW,
            text            = '',
            units           = PARAMS['stimuli']['answers']['left']['units'],
            pos             = PARAMS['stimuli']['answers']['left']['pos'],
            height          = PARAMS['stimuli']['answers']['left']['height'],
            color           = PARAMS['stimuli']['answers']['left']['color'],
            font            = PARAMS['stimuli']['answers']['left']['font']
        )
        self.RIGHT_ANSWER = visual.TextStim(self.EXP_WINDOW,
            text            = '',
            units           = PARAMS['stimuli']['answers']['right']['units'],
            pos             = PARAMS['stimuli']['answers']['right']['pos'],
            height          = PARAMS['stimuli']['answers']['right']['height'],
            color           = PARAMS['stimuli']['answers']['right']['color'],
            font            = PARAMS['stimuli']['answers']['right']['font']
        )
        self.UP_ANSWER = visual.TextStim(self.EXP_WINDOW,
            text            = '',
            units           = PARAMS['stimuli']['answers']['up']['units'],
            pos             = PARAMS['stimuli']['answers']['up']['pos'],
            height          = PARAMS['stimuli']['answers']['up']['height'],
            color           = PARAMS['stimuli']['answers']['up']['color'],
            font            = PARAMS['stimuli']['answers']['up']['font']
        )
        self.DOWN_ANSWER = visual.TextStim(self.EXP_WINDOW,
            text            = '',
            units           = PARAMS['stimuli']['answers']['down']['units'],
            pos             = PARAMS['stimuli']['answers']['down']['pos'],
            height          = PARAMS['stimuli']['answers']['down']['height'],
            color           = PARAMS['stimuli']['answers']['down']['color'],
            font            = PARAMS['stimuli']['answers']['down']['font']
        )
        # load the movie and make sure the volume is 0.
        self.MOVIE = visual.MovieStim2(self.EXP_WINDOW,
            filename ='LipReadingVN45/boast.mp4',
            volume = 0.0,
            pos = PARAMS['stimuli']['movie']['pos'],
            size = PARAMS['stimuli']['movie']['size']
        )

    def run_experiment(self):

        # the main experiment loop, which runs all the phases of the experiment
        # each phase is its own function

        # Do we want to try to connect to and communicate with NetStation during this run?
        # NetStation distilled example: https://github.com/gaelen/python-egi/blob/master/example_simple_distilled.py#L4
        # All the EEG stuff is called within the functions of the experiment phases
        # all netstation functionality is contained in netstation_xyz functions
        # if self.UseNetStation is false, these fctns will be called but not actually invoke
        # netstation commands (this would likely result in errors to connect)
        self.UseNetStation = False

        self.setup_experiment()
        self.display_instructions()
        self.do_task('baseline staircase')
        #self.break_for_main_staircase() # waits for user - ad added 2/9/17
        self.do_task('main staircase')
        self.end_experiment()

    # Functions for netstation operation.... ad 2/8/16
    def netstation_initialize(self):
        # Initiate NetStation if required
        if self.UseNetStation:
            self.ms_localtime = egi.ms_localtime
            self.ns = egi.NetStation()
            NetStationIPAddress = '11.0.0.42' # fix me
            NetStationPort = 55513 # probably uses this default
            self.ns.connect(NetStationIPAddress,NetStationPort)
            self.ns.BeginSession()
            self.ns.sync()
            self.ns.StartRecording()

    def netstation_sendtrigger(self,label,timestamp,table):
        if self.UseNetStation:
            self.ns.send_event( 'evt_', label=label, timestamp=timestamp, table = table )
            #self.ns.send_event( 'evt_', label="event", timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} )

    def netstation_finish(self):
        # Disconnect from the egi NetStation if we've been using it...
        if self.UseNetStation:
            self.ns.StopRecording()
            self.ns.EndSession()
            self.ns.disconnect()

    def setup_experiment(self):

        # things we need to do before the experiment begins. Note that we do not preload
        # all of the stimuli here. It is much less memory intensive to handle them one
        # at a time in the inter-trial interval (1 second is plenty of time to do this)
        # only when they are needed. here we get the monitor refresh rate (used to calculate jitter window)
        # and also set the mouse visibility and build the staircases we are going to need
        self.EXP_WINDOW.mouseVisible = PARAMS['devices']['mouse']['visible']
        self.ACTUAL_REFRESH_RATE = self.EXP_WINDOW.getActualFrameRate(nMaxFrames = 100, nWarmUpFrames = 20, threshold = 1)
        self.STIMS = yaml.safe_load(open("Wordlists/"+PARAMS['experiment info']['user-input']['wordlist'], 'r'))

        # initialize netstation if necessary....
        self.netstation_initialize()

        # These track accuracy for the given block - separately for hard and easy trials.
        self.hard_accuracy = [] #
        self.easy_accuracy = [] #
        self.hard_intensities = []
        self.easy_intensities = []

        # These help us keep track of duplicate stimuli
        self.recently_used_targets = []
        self.recently_used_stimsets = []

        # generate the stiarcase for this experiment from the parameter file
        self.build_the_staircases(PARAMS['staircases'])

        # setup a data folder for the subject's sound files
        os.mkdir(self.EXPERIMENT_DATA.dataFileName)

    def display_instructions(self):

        # for each of the instruction pages (params.yaml), set the correct text, draw them to the screen, and
        # flip the window to display them.  Wait for the 'space' key to move on.
        for instructions in PARAMS['stimuli']['instructions']['pages']:
            self.INSTRUCTIONS.setText(instructions)
            self.INSTRUCTIONS.draw()
            self.EXP_WINDOW.flip()
            event.waitKeys(PARAMS['devices']['keyboard']['keys next'])

    #def break_for_main_staircase(self):
    #        self.INSTRUCTIONS.setText("Begin recording EEG in preparation for main staircase. Press space to begin.")
    #        self.INSTRUCTIONS.draw()
    #        self.EXP_WINDOW.flip()
    #        event.waitKeys(PARAMS['devices']['keyboard']['keys next'])

    def manually_modify_intensity(self,which_staircase,this_step,easy,hard,unmodified_loudness_pow,blocktrial):
        Verbose = True
        #old_loudness = unmodified_loudness # so we can print to user...
        new_loudness_pow = unmodified_loudness_pow # by default
        step_size_db = .5 # how much to adjust stimulus loudness up or down - this will be applied in dB
        min_loudness_pow = 0.05 # units treated as magnitude/power/whatever/notDB
        min_loudness_db = (20 * math.log(min_loudness_pow,10))
        if Verbose == True: print "--------------"
        if Verbose == True: print "Evaluating trial in manually_modify_intensity()..."
        if which_staircase == 'main staircase': # 'baseline staircase':
            if Verbose == True: print "We ARE in the main staircase, so evaluating for loudness modification..."
            if this_step['label'] == 'easy': # then we're operating on easy trials
                trialdiff = "easy"
                TrialN = easy.thisTrialN
                old_loudness_pow = self.easy_intensities[-1] # this also will carry over the last element from baseline to main staircase.
                if TrialN == 0:
                    # THIS IS NEW
                    condition = self.CONDITION
                    easy, hard = self.STAIRCASE_HANDLER['baseline staircase'][condition].staircases
                    old_loudness_pow = easy.intensities[-1]
                    if Verbose == True: print "Trial 0, so starting with intensity",old_loudness_pow,"from end of easy baseline staircase for",condition
                    # END NEW.
                    self.easy_accuracy = []
                    self.easy_intensities = [] # clear the variable (after we've retrieved the last element from baseline)
                    if Verbose == True: print "First easy trial of new block, so clearing accuracy and intensity values for easy trials at beginning of block."
                if TrialN > 5:
                    avg_acc = np.mean(self.easy_accuracy[-5:]) # NB: ONLY CALCULATE ACC FROM LAST 5 ELEMENTS
                    if Verbose == True: print "Trial", TrialN,"easy average accuracy =",avg_acc,"..."
                    if avg_acc > .80: # then make the stimulus harder
                        old_loudness_db = 20 * math.log(old_loudness_pow,10) # old loudness is in magnitude, so conver to db
                        new_loudness_db = old_loudness_db - step_size_db
                        if new_loudness_db > min_loudness_db:
                            new_loudness_pow = 10**(new_loudness_db/20) # convert the new loudness back into magnitude so we can mix the trial's sound
                        else:
                            new_loudness_pow = min_loudness_pow
                        if Verbose == True: print "Acc on easies is > 85pct so making trial HARDER: old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
                    elif avg_acc == .8: # then don't change the loudness.
                        print "subject at 80 percent accuracy on this easy trial, not changing intensity"
                        new_loudness_pow = old_loudness_pow
                    else: # make stim easier
                        old_loudness_db = 20 * math.log(old_loudness_pow,10) # old loudness is in magnitude, so conver to db
                        new_loudness_db = old_loudness_db + step_size_db
                        if new_loudness_db > min_loudness_db:
                            new_loudness_pow = 10**(new_loudness_db/20) # convert the new loudness back into magnitude so we can mix the trial's sound
                        else:
                            new_loudness_pow = min_loudness_pow
                        if Verbose == True: print "Acc on easies is < 85pct so making trial EASIER: old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
                else:
                    new_loudness_pow = old_loudness_pow # force to stay the same the first 5 trials...
                    if Verbose == True: print "Trial number (easy) is only",TrialN,"so not modifying loudness (we start after trial 5) - ","old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
            else: # we're operating on hard trials.
                trialdiff = "hard"
                TrialN = hard.thisTrialN
                old_loudness_pow = self.hard_intensities[-1] # this also will carry over last element from baseline to main staircase
                if TrialN == 0:
                    # THIS IS NEW
                    condition = self.CONDITION
                    easy, hard = self.STAIRCASE_HANDLER['baseline staircase'][condition].staircases
                    old_loudness_pow = hard.intensities[-1]
                    if Verbose == True: print "Trial 0, so starting with intensity",old_loudness_pow,"from end of easy baseline staircase for",condition
                    # END NEW.
                    self.hard_accuracy = []
                    self.hard_intensities = [] # clear the variable (after we've retrieved the last element from baseline)
                    if Verbose == True: print "First hard trial of new block, so clearing accuracy and intensity values for hard trials at beginning of block."
                if TrialN > 5:
                    avg_acc = np.mean(self.hard_accuracy[-5:]) # NB: ONLY CALCULATE ACC FROM LAST 5 ELEMENTS
                    if Verbose == True: print "Trial", TrialN,"hard average accuracy =",avg_acc,"..."
                    if avg_acc > .4: # then make the stimulus harder
                        old_loudness_db = 20 * math.log(old_loudness_pow,10) # old loudness is in magnitude, so conver to db
                        new_loudness_db = old_loudness_db - step_size_db
                        print "old loud pow",old_loudness_pow,"old loud db",old_loudness_db,"new loudness db=",new_loudness_db
                        if new_loudness_db > min_loudness_db:
                            new_loudness_pow = 10**(new_loudness_db/20) # convert the new loudness back into magnitude so we can mix the trial's sound
                            print "new loudness db >0 so calcluating new loudness pow=",new_loudness_pow
                        else:
                            new_loudness_pow = min_loudness_pow
                            print "new loudness db <= so new loudness pow is min_loudness_pow",min_loudness_pow
                        if Verbose == True: print "Acc on hards is > 45pct so making trial HARDER: old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
                    elif avg_acc == .4: # then don't change the loudness.
                        print "subject at 40 percent accuracy on this hard trial, not changing intensity"
                        new_loudness_pow = old_loudness_pow
                    else: # make the stimulus easier
                        old_loudness_db = 20 * math.log(old_loudness_pow,10) # old loudness is in magnitude, so conver to db
                        new_loudness_db = old_loudness_db + step_size_db
                        print "old loud pow",old_loudness_pow,"old loud db",old_loudness_db,"new loudness db=",new_loudness_db
                        if new_loudness_db > min_loudness_db:
                            new_loudness_pow = 10**(new_loudness_db/20) # convert the new loudness back into magnitude so we can mix the trial's sound
                            print "new loudness db >0 so calcluating new loudness pow=",new_loudness_pow
                        else:
                            new_loudness_pow = min_loudness_pow
                            print "new loudness db <= so new loudness pow is min_loudness_pow",min_loudness_pow
                        if Verbose == True: print "Acc on hards is < 45pct so making trial EASIER: old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
                else:
                    new_loudness_pow = old_loudness_pow # force to stay the same the first 5 trials...
                    if Verbose == True: print "Trial number (hard) is only",TrialN,"so not modifying loudness (we start after trial 5) - ","old intensity=",old_loudness_pow,"new intensity=",new_loudness_pow
        else:
            if Verbose == True: print "We are not in the main staircase at all, so not modifying loudness."
        return new_loudness_pow

    def do_task(self, which_staircase):
        # if this is the main staircase, pull the values from the baseline staircases
        # to use as start values in the main staircase
        #if which_staircase == 'main staircase':
        #    self.get_baseline_thresholds() # This is outmoded by manually_modify_intensity() which overrides anything this does.

        # create a variable to hold what block number we are on
        this_block = 0

        # for all of the blocks in the available staircases
        for block in self.randomize_blocks(which_staircase):
            this_block += 1
            self.CONDITION = block
            # enter the staircase and let the data handler know we have done so
            this_staircase = self.STAIRCASE_HANDLER[which_staircase][block]

            self.EXPERIMENT_DATA.addLoop(this_staircase)

            # show which block we are doing (Auditory, Visual, Environmental)
            self.display_block_title_screen(self.CONDITION)

            # for all of the trials that we are supposed to do per block in this stiarcase
            for trial in range(PARAMS['method']['reps'][which_staircase]['trials per block']):
                # add some data about which condition and block it is
                this_staircase.addOtherData('condition', self.CONDITION)
                this_staircase.addOtherData('block', this_block)

                # get the loudness we should set stim at and the params of this step in the staircase
                # this_loudness == "trial_volume" in intertrial_interval() function
                # and this_step == "trial_params"
                this_loudness, this_step = this_staircase.next()

                #easy, hard = self.STAIRCASE_HANDLER['main staircase'][block].staircases
                easy, hard = self.STAIRCASE_HANDLER[which_staircase][block].staircases

                ################################################################################################################

                # Get previous intensities and accuracies for this staircase, condition, and difficulty label
                stairkey = which_staircase+self.CONDITION+this_step["label"] # e.g. 'main staircaseAuditoryhard'
                previous_intensities = self.tracked_intensities[stairkey]
                previous_accuracies = self.tracked_accuracies[stairkey]

                stepSize = .5 # this is in decibles!
                intensity_modification = 0 # default to keeping it the same.

                # Figure out the condition type, and let's pull trial n and cutoffs
                if this_step["label"] == "easy":
                    CurTrial = easy.thisTrialN
                    accuracy_cutoff = .8
                else:
                    CurTrial = hard.thisTrialN
                    accuracy_cutoff = .4

                print "================"
                print "Presenting",which_staircase,"block",block,"block#",this_block,"trial",trial,", which is", this_step["label"],"trial #",CurTrial

                old_loudness_pow = this_loudness
                if which_staircase == 'main staircase': #'main staircase':
                    print "In main staircase, so considering whether to modify loudness."
                    if CurTrial == 0: # Then start with last baseline trial for this condition and label.
                        blstairkey = 'baseline staircase'+self.CONDITION+this_step["label"]
                        old_loudness_pow = self.tracked_intensities[blstairkey][-1]
                        intensity_modification = 0 # do not modify
                    elif CurTrial < 5: # Then set loudness to the most recent loudness value.
                        old_loudness_pow = previous_intensities[-1]
                        intensity_modification = 0 # do not modify
                        print "Condition/diff trial number is",CurTrial, "which is < 5, so just holding loudness constant."
                    else:
                        print "Condition/diff trial is", CurTrial, "which is >= 5, so now seeing if we're on an even trial (since we only evaluate modifications every other trial)"
                        old_loudness_pow = previous_intensities[-1]
                        if CurTrial % 2 == 0: #  modulus to check trial evenness
                            # Start by getting the average of the most recent 5 trials....
                            AvgRecentTrials = np.mean(previous_accuracies[-5:]) # Average acc of last 5 trials.
                            print "This is an even trial number for this condition, so evaluating accuracy for need to modify loudness"
                            if AvgRecentTrials < accuracy_cutoff:
                                intensity_modification = 1 * stepSize # increase by 1 step
                                print "Recent accuracy",AvgRecentTrials,"is below cutoff",accuracy_cutoff,"so making easier by modifying loudness by",intensity_modification
                            elif AvgRecentTrials == accuracy_cutoff:
                                intensity_modification = 0 # do not modify
                                print "Recent accuracy",AvgRecentTrials,"is exacty at cutoff",accuracy_cutoff,"so doing nothing (modifying loudness by",intensity_modification,")"
                            else:
                                intensity_modification = -1 * stepSize
                                print "Recent accuracy",AvgRecentTrials,"exceeds cutoff",accuracy_cutoff,"so making harder modifying loudness by",intensity_modification
                        else: # it's an odd trial, so use the previous trial's intensity and do not modify it.
                            intensity_modification = 0 # do not modify
                            print "This is an odd trial number for this condition, so holding loudness the same."
                            # < HOLD LOUDNESS SAME!
                else: # we're in baseline staircase...
                    print "In the baseline staircase, so doing nothing."

                print "scheduled intensity modification is",intensity_modification
                # Now do the modification
                old_loudness_db = 20 * math.log(old_loudness_pow,10) # old loudness is in magnitude, so convert to db
                new_loudness_db = old_loudness_db + intensity_modification
                new_loudness_pow = 10**(new_loudness_db/20) # Convert the new loudness in dB back into magnitude so we can mix the trial's sound

                this_loudness = round(new_loudness_pow,4)
                print "On this trial, old loudness was",round(old_loudness_pow,4),"and new loudness was",round(new_loudness_pow,4)

                ################################################################################################################

                # do each portion of the trail
                ###########################################

                self.intertrial_interval(this_loudness, this_step)

                fastTesting = False # Skip most of the experiment if we're testing...
                if not fastTesting: # ad - remove this - it's for testing
                #    self.difficulty_cue_period(this_step) # ad 2/8/17
                    #self.prestimulus_period(this_step)
                    self.stimulus_presentation_window()
                    self.poststimulus_waiting_period()
                    is_correct = self.answer_choice_period() # return is correct
                else:# ad - remove this - it's for testing
                    is_correct = random.uniform(0, 1) > .25 # ad - remove this - it's for testing
                ###########################################

                # tell the staircase whether we got this step right
                this_staircase.addResponse(is_correct)

                # Save this so we can manipulate the difficult in the main staircase - ad
                Verbose = True
                if is_correct == True:
                    corr_num = 1
                else:
                    corr_num = 0

                # Accumulate accuracy values and intensity values - ad 2/25/17
                oldval = self.tracked_accuracies[stairkey]
                oldval.append(corr_num)
                self.tracked_accuracies[stairkey] = oldval
                oldval = self.tracked_intensities[stairkey]
                oldval.append(this_loudness)
                self.tracked_intensities[stairkey] = oldval

                if Verbose == True: print "Results of this",this_step["label"],"trial: appended intensity",this_loudness,"to stored intensities:",self.tracked_intensities[stairkey]
                if Verbose == True: print "Results of this",this_step["label"],"trial: appended accuracy",corr_num,"to stored accuracies:",self.tracked_accuracies[stairkey]

                # Save some info about this trial for outputting - ad 2/25/17
                self.EXPERIMENT_DATA.addData('current_staircase', which_staircase)
                self.EXPERIMENT_DATA.addData('current_condition', block) # self.CONDITION)
                self.EXPERIMENT_DATA.addData('current_manual_loudness', this_loudness)
                #self.EXPERIMENT_DATA.addData('Nblock', block)
                self.EXPERIMENT_DATA.addData('current_block_n', this_block)
                self.EXPERIMENT_DATA.addData('current_block_trial_n', trial)
                self.EXPERIMENT_DATA.addData('current_condition_trial_n', CurTrial)
                self.EXPERIMENT_DATA.addData('current_diff', this_step["label"])
#                print "Presenting",which_staircase,"block",block,"block#",this_block,"trial",trial,", which is", this_step["label"],"trial #",CurTrial

                # tell the data handler that we are finshed with that trial and about to start a new trial
                self.EXPERIMENT_DATA.nextEntry()

                # if somebody presses escape on any trial, quit the experiment
                if event.getKeys(PARAMS['devices']['keyboard']['keys quit']): self.end_experiment()

            # if this is a block we are supposed to take a rest after, do so
            #if this_block in PARAMS['method']['reps'][which_staircase]['rest after blocks']:
                #if not fastTesting: # ad - remove this - it's for testing
                    #self.do_rest_period()

    def end_experiment(self):

        # this is just a cleanup function that closes the experiemnt
        # window and quits psychopy

        self.netstation_finish()

        self.EXP_WINDOW.close()
        core.quit()

    def randomize_blocks(self, which_staircase):

        # Take each condition (Auditory, Visual, Environmental) and randomly
        # permute them however many times are specified in number of blocks per condition.
        BLOCKS = []
        for _ in range(PARAMS['method']['reps'][which_staircase]['blocks per condition']):
            for condition in numpy.random.permutation(PARAMS['experiment info']['user-input']['conditions']): BLOCKS.append(condition)

        # returns the list of randomized blocks for the staircase
        return BLOCKS

    def display_block_title_screen(self, this_condition):

        # set the text for the particular block, draw it to the screen and flip
        # the window.  Wait for the time specified in 'block title screen'
        self.BLOCK_TITLE.setText(this_condition)
        self.BLOCK_TITLE.draw()
        self.EXP_WINDOW.flip()
        core.wait(PARAMS['method']['timing']['block title screen'])

    def build_the_staircases(self, all_staircases):

        # here we build all of the staircases we will use in the experiment.  This is handled by creating a
        # MultiStairHandler for each condition (Auditory, Visual, and Environmental).  Each multistair
        # has an easy and a hard staircase, and they are interleaved (selected at random such that not more than
        # three of the same difficulty level are selected in a row).  All staircases are QUEST adaptive staircases
        # with parameters set from the params.yaml file

        # make an empty dictionary to hold the staircases
        self.STAIRCASE_HANDLER = {}

        # This is a hack to track values - ad 2/25/17
        self.tracked_intensities = dict() # so we can manually manipulate the intensity values...
        self.tracked_accuracies = dict() # so we can manually manipulate the intensity values...

        # for all of the staircases (in params - baseline and main)
        for staircase in all_staircases:

            # create an empty dictionary
            self.STAIRCASE_HANDLER[staircase] = {}

            # and add a multistair handler for each condition (Auditory, Visual, and Environmental)
            for condition in PARAMS['experiment info']['user-input']['conditions']:
                self.STAIRCASE_HANDLER[staircase].update({condition: data.MultiStairHandler(
                        stairType = 'simple', # not QUEST
                        method = 'sequential',
                        conditions = [PARAMS['staircases'][staircase][condition]['easy'], PARAMS['staircases'][staircase][condition]['hard']],
                        nTrials = PARAMS['method']['reps'][staircase]['trials per staircase']
                        )})

                # This is a hack to track values - ad 2/25/17
                easykey = staircase+condition+'easy' # so we can manually manipulate the intensity values...
                hardkey = staircase+condition+'hard' # so we can manually manipulate the intensity values...
                self.tracked_intensities[easykey] = list() # so we can manually manipulate the intensity values...
                self.tracked_intensities[hardkey] = list() # so we can manually manipulate the intensity values...
                self.tracked_accuracies[easykey] = list() # so we can manually manipulate the intensity values...
                self.tracked_accuracies[hardkey] = list() # so we can manually manipulate the intensity values...

    def intertrial_interval(self, trial_volume, trial_params):

        # start the precise timer
        self.start_precise_timer(PARAMS['method']['timing']['intertrial interval'])

        # draw the fixation cross in gray and flip the window
        self.FIXATION_CROSS.setColor('gray')
        self.FIXATION_CROSS.draw()
        self.EXP_WINDOW.flip()

        # preload the stimuli we need for this trial during this time.
        self.preload_stimulus(trial_volume, trial_params)

        # stop the precise timer and save whether it was accurate on this trial
        timer_accuracy = self.stop_precise_timer()
        self.EXPERIMENT_DATA.addData('intertrial_interval', timer_accuracy)

    #def difficulty_cue_period(self,trial_params): # added ad 2/8/17
       # start precise timer
    #    self.start_precise_timer(PARAMS['method']['timing']['difficulty cue duration'])

        # set which text will appear on the screen
    #    if trial_params['label'] == 'easy': diff_text = 'Easy' # updated ad 2/8/17
    #    else: diff_text = 'Hard' # updated ad 2/8/16

        # draw the E or the H and flip the window
    #    self.DIFFICULTY_TEXT.setText(diff_text)
    #    self.DIFFICULTY_TEXT.draw()
    #    self.EXP_WINDOW.flip()

        # stop the precise timer and save whether it was accurate on this trial
    #    timer_accuracy = self.stop_precise_timer()
    #    self.EXPERIMENT_DATA.addData('difficulty_cue_period', timer_accuracy)

    #def prestimulus_period(self, trial_params):

        # start the precise timer
    #    self.start_precise_timer(PARAMS['method']['timing']['prestimulus period'])

        # start playing the mixed sound file
    #    self.STIMULUS_SOUND.play()

        # draw the fixation cross in gray and flip the window
    #    self.FIXATION_CROSS.setColor('gray')
    #    self.FIXATION_CROSS.draw()
    #    self.EXP_WINDOW.flip()

        # set which text will appear on the screen
        #if trial_params['label'] == 'easy': diff_text = 'Easy' # updated ad 2/8/17
        #else: diff_text = 'Hard' # updated ad 2/8/16

        # draw the E or the H and flip the window
        #self.DIFFICULTY_TEXT.setText(diff_text)
        #self.DIFFICULTY_TEXT.draw()
        #self.EXP_WINDOW.flip()


        # stop the precise timer and save whether it was accurate on this trial
    #    timer_accuracy = self.stop_precise_timer()
    #    self.EXPERIMENT_DATA.addData('prestimulus_period', timer_accuracy)

    def stimulus_presentation_window(self):

        # start the precise timer
        self.start_precise_timer(PARAMS['method']['timing']['stimulus presentation window'])

        # jitter the start time
        self.jitter_start_time()

        # fade in the stim depending on what we have got.
        # self.fade_in_stimulus()

        # send the trigger here probably
        #self.send_ttl_trigger('stim presentation window')

        # play the movie and/or sound and/or noisemask
        self.play_stimulus()

        # SEND TRIGGER for stimulus presentation window
        label = 'a'
        timestamp = 'self.ms_localtime'
        table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042}
        self.netstation_sendtrigger(label,timestamp,table)

        # stop the precise timer and save whether it was accurate on this trial
        timer_accuracy = self.stop_precise_timer()
        self.EXPERIMENT_DATA.addData('stimulus_presentation_window', timer_accuracy)

    def poststimulus_waiting_period(self):

        # start the precise timer
        self.start_precise_timer(PARAMS['method']['timing']['post stimulus waiting period'])

        # make the fixation cross red and draw it to the screen
        self.FIXATION_CROSS.setColor('red')
        self.FIXATION_CROSS.draw()
        self.EXP_WINDOW.flip()

        # SEND TRIGGER for poststimulus waiting period
        label = 'a'
        timestamp = 'self.ms_localtime'
        table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042}
        self.netstation_sendtrigger(label,timestamp,table)

        # stop the precise timer and save whether it was accurate on this trial
        timer_accuracy = self.stop_precise_timer()
        self.EXPERIMENT_DATA.addData('poststimulus_waiting_period', timer_accuracy)

    def answer_choice_period(self):

        # create a dictionary of answer positions (keys) assigned to
        # the text stims in those positions (values)
        ANSWER_POSITIONS = {
            'left': self.LEFT_ANSWER,
            'right': self.RIGHT_ANSWER,
            'up': self.UP_ANSWER,
            'down':self.DOWN_ANSWER
        }

        # randomly shuffle the answer choices and assign them to ANSWER_POSITIONS
        # draw each one and then flip the window after all 4 are drawn
        numpy.random.shuffle(self.ANSWER_CHOICES)
        for pos in ANSWER_POSITIONS.itervalues():
            this_answer = self.ANSWER_CHOICES.pop()
            ans = str.replace(this_answer, "_", " ")
            pos.setText(ans)
            pos.draw()
        self.EXP_WINDOW.flip()

        # SEND TRIGGER for nbeginning of answer choice period display
        label = 'a'
        timestamp = 'self.ms_localtime'
        table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042}
        self.netstation_sendtrigger(label,timestamp,table)

        # add this to remove underscores from the correct answer
        correct_answer = str.replace(self.TRIAL_SOUND, "_", " ")

        # wait for the participant to press a key (for time specified in timeout)
        # return the key they pressed and their reaction time (RT)
        # return whether their choice was correct (for data storing purposes)
        try:
            # get response from keyboard? or the gamepad?
            selection, RT = event.waitKeys(maxWait=PARAMS['method']['timing']['answer choice timeout'], keyList=ANSWER_POSITIONS.keys(), timeStamped = True)[0]
            this_choice = ANSWER_POSITIONS[selection].text
            if this_choice == correct_answer: is_correct = True
            else: is_correct = False
        except TypeError:
            selection, RT, this_choice = ['NA'] * 3
            is_correct = False

        # add the data we have collected to the data manager
        self.EXPERIMENT_DATA.addData('correct_answer', correct_answer)
        self.EXPERIMENT_DATA.addData('answer_choice_position', selection)
        self.EXPERIMENT_DATA.addData('answer_choice', this_choice)
        self.EXPERIMENT_DATA.addData('is_correct', is_correct)
        self.EXPERIMENT_DATA.addData('RT', RT)

        return is_correct

    def play_stimulus(self):
        # if we are at the movie, play it.  otherwise draw noise
        if self.CONDITION == "Visual":
            # self.MOVIE.seek(0.0)
            # self.MOVIE.setVolume(0.0)

            # play the word and the movie at the same time
            # self.WORD.play()
            self.MOVIE.play()

            # while the movie is still playing, draw it
            while self.MOVIE.status != visual.FINISHED:
                self.MOVIE.draw()
                self.EXP_WINDOW.flip()

        else:
            # play the word and the image mask at the same time
            # self.WORD.play()
            self.IMAGE_MASK.draw()
            self.EXP_WINDOW.flip()

    def preload_stimulus(self, trial_volume, trial_params):
        # this function preloads the stimuli necessary for the trial.  Note that it always loads the corresponding video
        # and an image mask to make it equal for both trials.  But it only uses one later on.
        # randomly choose a sound the play from the remaining trials in this staircase

        doCheckForDuplicates = True # check for duplicate stimuli in this trial?
        Verbose = True # dont' show debug info

        if doCheckForDuplicates == False: # then just pull the next stimulus at random -- this is the old code.
            remaining_trials = self.STIMS[trial_params['staircasename']][trial_params['condition']][trial_params['label']]
            self.ANSWER_CHOICES = remaining_trials.pop(numpy.random.choice(remaining_trials.keys()))
            self.TRIAL_SOUND = self.ANSWER_CHOICES[0]
        else: # check for duplicates in the last blocks's stimuli...
            isStimulusNew = False # default to False - we need to find a new stimulus to break the while loop.
            remaining_trials = self.STIMS[trial_params['staircasename']][trial_params['condition']][trial_params['label']] # retrieve all remaining stimuli

            # Get info for most recent 20 stimuli - we'll use this to make sure we don't have repeats
            last_twenty_item_slices = slice(-20,None) # nb slice object
            mostRecentlyUsedStimulusSets = self.recently_used_stimsets[last_twenty_item_slices] # remember this list is sorted and joined stimulus sets
            mostRecentlyUsedTargets = self.recently_used_targets[last_twenty_item_slices]
            nDuplicatesFound = 0 # we'll keep track of how many duplicates we encounter to break an infinite loop.
            while isStimulusNew == False:
                randomRemainingTrialKey = numpy.random.choice(remaining_trials.keys()) # Start with a random number n
                stimulusSetToCheck = remaining_trials[randomRemainingTrialKey] # extract the actual item set to check.

                # We need to make sure two things:
                # 1) the target item did not occur in the past 20 items
                # 2) the alphabetized stimulus choices (all 4) did not occur together in the past 20 items

                if Verbose == True :  print "Stimulus set drawn at random:",stimulusSetToCheck

                currentTargetItemToCheck = stimulusSetToCheck[0] # new item to check
                currentSetToCheck = ''.join(sorted(stimulusSetToCheck)) # this takes ['zz','basd','vvv'] -> 'basdvvvzz' (turn set into one unique string)

                if Verbose == True :  print "Stimulus tentatively selected for this trial:", currentTargetItemToCheck, "with options", stimulusSetToCheck
                if Verbose == True :  print "Checking to see if target", currentTargetItemToCheck, "occured in the last 20 trials:", mostRecentlyUsedTargets
                if Verbose == True :  print "Checking to see the whole set", currentSetToCheck, "occured in the last 20 trials:", mostRecentlyUsedStimulusSets

                if (
                    not any(currentTargetItemToCheck in item for item in mostRecentlyUsedTargets) and
                    not any(currentSetToCheck in item for item in mostRecentlyUsedStimulusSets)
                    ):
                    if Verbose == True :  print "> Not a duplicate." # if we get here, then there's no recent duplication, so we can use this stimulus...
                    isStimulusNew = True # so we don't loop forever.


                else: # we found a duplicate...
                    if Verbose == True :  print("> Encountered a duplicate. Trying new item...")
                    nDuplicatesFound=nDuplicatesFound+1
                    if nDuplicatesFound > 25: # did we fail to find a new stimulus 25 times?
                        if Verbose == True :  print "Encountered > 25 duplicates, breaking the loop and using what we have..."
                        isStimulusNew = True # this is a lie, but we use it to avoid infinite loops...


            # Whatever came out of our loop -- we now use those values...
            self.ANSWER_CHOICES = remaining_trials.pop(randomRemainingTrialKey) # Peel it off the list for real
            self.TRIAL_SOUND = self.ANSWER_CHOICES[0] # It's the sound we'll play.

            # Store our new target and set so we can tell if we repeat it in the future...
            self.recently_used_targets.append(currentTargetItemToCheck)
            self.recently_used_stimsets.append(currentSetToCheck)

        if Verbose == True :  print "loading ", self.TRIAL_SOUND
        if Verbose == True :  print "remaining trials ", remaining_trials

        # load the movie you'll need and set the volume to 0
        if self.CONDITION == "Visual":
            self.MOVIE.loadMovie('LipReadingVN45/'+self.TRIAL_SOUND+'.mp4')
            self.MOVIE.setVolume(0.0)

        # load the image mask
        list_of_distorted_faces = glob.glob('Facemorphs/*.jpg')
        self.IMAGE_MASK.image = numpy.random.choice(list_of_distorted_faces)
        # print numpy.random.choice(list_of_distorted_faces) #ad
        # self.IMAGE_MASK.setTex(numpy.random.random((64,64))) 01/12

        # pull the actual sound file to retrieve duration
        which_sound_file = 'Sounds/'+trial_params['condition']+'/'+trial_params['label']+'/'+self.TRIAL_SOUND+'.wav'
        name_saved_sound = self.EXPERIMENT_DATA.dataFileName+'/'+PARTICIPANT_INFO['subject']+'-'+trial_params['condition']+'-'+trial_params['staircasename']+'-'+trial_params['label']+'-'+self.TRIAL_SOUND+'-vol-'+str(trial_volume)+'.wav'

        # get the duration of the sound and calculate jitter
        self.THIS_TRIAL_SOUND.setSound(which_sound_file)
        self.calculate_jitter(self.THIS_TRIAL_SOUND.getDuration())

        # mix the sounds
        self.mix_sound_sox(noise_file = 'Sounds/noise.wav',
            noise_volume = 1.0,
            stimulus_file = 'Sounds/'+trial_params['condition']+'/'+trial_params['label']+'/'+self.TRIAL_SOUND+'.wav',
            stimulus_volume = trial_volume,
            output_file_name = name_saved_sound)

        # preload the output sound and set it to full volume
        self.STIMULUS_SOUND.setSound(name_saved_sound)
        self.STIMULUS_SOUND.setVolume(1.0)

        #print trial_volume, trial_params #ad

    # This function uses subprocess.Popen instead of os.system to invoke sox. here we are interested in pulling out the duration of the sound from
    # sox's info (--i) flag so that we don't have to rely un an incorrect Sound.getDuration()
    def getDurationSox(self,which_sound_file):
        verbose = 0
        #process = subprocess.Popen('sox --i C:\Users\Admin\Desktop\coffee.wav',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # get sox info about sound
        soxcommand = 'sox --i ' + which_sound_file
        if verbose: print "Querying sox for sound duration of " + which_sound_file + ' using command: ' + soxcommand
        process = subprocess.Popen(soxcommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # get sox info about sound
        rawoutput = process.communicate() # get the output
        outpt = rawoutput[0] # 0th element is the relevant output from sox
        #print "Output: " + outpt
        splitup = outpt.split(":")
        relevant_token = splitup[7] # time in seconds and milliseconds (SS.MS) is first space-delimeted token
        if verbose: print "Relevant token: " + relevant_token
        subtokens = relevant_token.split(" ")
        relevant_subtoken = subtokens[0] # now we have the string e.g., "01.03"
        if verbose: print "Found duration to be: " + relevant_subtoken
        self.CurrentSoundDuration = float(relevant_subtoken) # now a float, may need to take to int using int() if data type conflict
        print 'Current Sound Duration is:'
        print self.CurrentSoundDuration

    def mix_sound_sox(self, noise_file, noise_volume, stimulus_file, stimulus_volume, output_file_name):
        Verbose = True
        stimulus_padding = PARAMS['method']['timing']['prestimulus period'] + PARAMS['method']['timing']['fade movie buffer']+self.RANDOM_ONSET_TIME
        # nb: self.RANDOM_ONSET_TIME should always be less than 2.0 (so when added with the padding parameters, together, they do not add to > 4.0)
        if Verbose: print 'random onset time for this trial: '
        if Verbose: print self.RANDOM_ONSET_TIME
        currentOS = 'Windows'

        if currentOS == 'Windows': # use subprocess.call to mix sounds as opposed to os.system() to prevent the command window from popping up and stealing focus from psychopy

            # we are using subprocess.CALL as opposed to OPEN so that the process doesn't return control back
            # to python until it finishes (i.e. the file has been mixed and is available to be read back in in a few
            # clock cycles (the next command or two in mix_sound_sox()'s parent function)
            soxcommand = 'sox -V0 --combine mix -v '+str(noise_volume)+' '+noise_file+' -v '+str(stimulus_volume)+' "|sox '+stimulus_file+' -p pad '+str(stimulus_padding)+' " '+output_file_name
            process = subprocess.call(soxcommand,shell=True) # ,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # mixing sound in sox

        else: # pipe in sox in one line
            if Verbose: # then use default verbosity (-V2)
               cmd = 'sox -V3 --combine mix -v '+str(noise_volume)+' '+noise_file+' -v '+str(stimulus_volume)+' "|sox '+stimulus_file+' -p pad '+str(stimulus_padding)+' " '+output_file_name
               print cmd
               os.system(cmd)
            else: # show nothing:( -V0)
               os.system('sox -V0 --combine mix -v '+str(noise_volume)+' '+noise_file+' -v '+str(stimulus_volume)+' "|sox '+stimulus_file+' -p pad '+str(stimulus_padding)+' " '+output_file_name)


  #  def mix_sound_sox(self, noise_file, noise_volume, stimulus_file, stimulus_volume, output_file_name):
   #     Verbose = True
    #    stimulus_padding = PARAMS['method']['timing']['prestimulus period'] + PARAMS['method']['timing']['fade movie buffer']+self.RANDOM_ONSET_TIME
        #print stimulus_padding #ad

     #   if Verbose: # then use default verbosity (-V2)
      #      os.system('sox -V --combine mix -v '+str(noise_volume)+' '+noise_file+' -v '+str(stimulus_volume)+' "|sox '+stimulus_file+' -p pad '+str(stimulus_padding)+' " '+output_file_name)
       # else: # show nothing:( -V0)
        #    os.system('sox -V0 --combine mix -v '+str(noise_volume)+' '+noise_file+' -v '+str(stimulus_volume)+' "|sox '+stimulus_file+' -p pad '+str(stimulus_padding)+' " '+output_file_name)

    def start_precise_timer(self, duration):

        self.timer = core.StaticPeriod(screenHz = PARAMS['devices']['monitor']['screenHz'])
        self.timer.start(duration)

    def stop_precise_timer(self):

        timer_accuracy = self.timer.complete()
        self.EXP_WINDOW.flip()

        # returns the accuracy of the timer
        return timer_accuracy

    def calculate_jitter(self, stim_duration):

        # get the variables we need to calculate the jitter
        jitter_window = PARAMS['method']['timing']['stimulus presentation window']
        offset_buffer = PARAMS['method']['timing']['stimulus offset buffer']
        seconds_per_frame = 1/PARAMS['devices']['monitor']['screenHz']

    #    print self.TRIAL_SOUND, stim_duration #ad
    #    print jitter_window, offset_buffer, seconds_per_frame #ad

        # take the stimuli duration and figure out possible start times that would end
        # within the stim presntation window.  use a bugger to make sure we don't cut it too close
        # to the end of the window
        possible_jitter = (jitter_window - offset_buffer) - stim_duration
        possible_onset_times = numpy.arange(seconds_per_frame, possible_jitter, seconds_per_frame)

        #  print possible_jitter, possible_onset_times #ad

        # choose a random onset time from these options and return it
        # try:
        self.RANDOM_ONSET_TIME = numpy.random.choice(possible_onset_times)
        # except ValueError:
        #     print "Sorry, the current stimulus is too long to play in the stimulus presentation window"
        # while we are waiting, add the actual onset and offset times to the data filename
        self.EXPERIMENT_DATA.addData('actual_onset_time', self.RANDOM_ONSET_TIME)
        self.EXPERIMENT_DATA.addData('actual_offset_time', self.RANDOM_ONSET_TIME + self.THIS_TRIAL_SOUND.getDuration())

        # print self.RANDOM_ONSET_TIME #ad


    def jitter_start_time(self):

        ISI = core.StaticPeriod()
        ISI.start(PARAMS['method']['timing']['fade movie buffer'] + self.RANDOM_ONSET_TIME)

        nFrames = PARAMS['method']['timing']['frames to fade movie']
        opacity_list = numpy.arange(0.0, 1.0, (1.0/nFrames))

        #print "nFRAMES ", nFrames, "OPACITY LIST ", opacity_list #ad
        #
        if self.CONDITION == "Visual":
        # cue up the movie, even if you aren't using it for timing consistency
            self.MOVIE.play()
            self.MOVIE.pause()

        for opacity in opacity_list:
            if self.CONDITION == "Visual": this_stim = self.MOVIE
            else: this_stim = self.IMAGE_MASK
            this_stim.setOpacity(opacity)
            this_stim.draw()
            self.EXP_WINDOW.flip()

        if self.CONDITION == "Visual":
            self.MOVIE.loadMovie('LipReadingVN45/'+self.TRIAL_SOUND+'.mp4')
            self.MOVIE.setVolume(0.0)


        ISI.complete()

    #def do_rest_period(self):

        # set the instructions for the rest period, draw them, and
        # wait for however long is specified in REST_BLOCK_DURATION
    #    self.INSTRUCTIONS.setText(PARAMS['stimuli']['instructions']['rest instructions'])
    #    self.INSTRUCTIONS.draw()
    #    self.EXP_WINDOW.flip()
    #    core.wait(PARAMS['method']['timing']['rest block duration'])

    def send_ttl_trigger(self, name = None):
        # this is not doing anything yet; here is where you would add the code to
        # send the ttl trigger.  It is likely very short, just a few lines
        # and you'll need to use psychopy's parallel library to send it
        pass

    def get_baseline_thresholds(self):
        print "GET_BASELINE_THRESHOLDS FUNCTION PRINTS:"
        thresholds = {}

        for condition in PARAMS['experiment info']['user-input']['conditions']:
            easy, hard = self.STAIRCASE_HANDLER['baseline staircase'][condition].staircases
            thresholds[condition] = {'easy': easy.intensities[-1], 'hard': hard.intensities[-1]}

        for condition in PARAMS['experiment info']['user-input']['conditions']:
            easy, hard = self.STAIRCASE_HANDLER['main staircase'][condition].conditions
            print easy, hard

            # NB: The following updates the staircases moving forward...
            easy['startVal'] = thresholds[condition]['easy']
            hard['startVal'] = thresholds[condition]['hard']

            print easy, hard
            print self.STAIRCASE_HANDLER['main staircase'][condition].conditions



exp = WordsInNoiseEEG()
exp.run_experiment()
