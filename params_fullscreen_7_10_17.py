---
# This is the parameter file for the words-in-noise-EEG experiment.
# It is a YAML file; Here is a good overview  (http://docs.ansible.com/ansible/YAMLSyntax.html)
# In general, you can edit anything after a colon (:)
# Descriptions of what each parameter does is provided in the comments
#UP_Down_Edit
experiment info:
    exp-name: words-in-noise-EEG            # The name of the expeirment
    data-path: data/                        # the folder where you want to save the data (must end in /)
    user-input:
        subject: ''                         # '' , provides a blank field for entering subject id (tags data file)
        gender:                             # provides a list of options for gender in gui
            - male
            - female
        hand:                               # provides a list of options for handedness in gui
            - left
            - right
        conditions:
            - [Auditory]
            - [Visual]
            - [Environmental]
            - [Phoneme]
            - [Phoneme, Environmental]
            - [Auditory, Visual]
            - [Auditory, Environmental]
            - [Auditory, Phoneme]
            - [Auditory, Environmental, Visual]
            - [Auditory, Environmental, Visual, Phoneme]
        wordlist:
            - FinalExperimentList.yaml
            - list1_adedits.yaml

devices:
    monitor:                                # sets the parameters for the visual.Window ()
        screen: 0                           # which screen we are using
        screenHz: 60.0                      # what is the refresh rate?
        size: [2560, 1440]                   # size of screen in pixels
        units: pix                          # screen units (pix)
        win type: pyglet                    # type of window (pyglet, pygame)
        background color: black             # what color is the background?
        full screen: True                  # True or False fullscreen
    mouse:
        visible: False                       # True or False mouse visible
    keyboard:
        keys quit: [escape]                 # Keys that will quit
        keys next: [space]
        keys eegbreak: [enter] # Keys that will move to the next thing (like for instructions)
method:
    # conditions:                             # a list of the conditions in the experiment
    #     - Auditory
    #     - Visual
    #     - Environmental
    reps:
        baseline staircase:
            blocks per condition: 2
            trials per block: 20             # number of trials to do in each block
            trials per staircase: 20         # number of trials
            rest after blocks: [2]       # blocks we should do rest after
        main staircase:
            blocks per condition: 10
            trials per block: 20
            trials per staircase: 100
            rest after blocks: [2,4,6,8,12,14,16,18] #removed rest after block 4 - this is end of baseline, need to have rest with keypress to advance after block 4
            eegbreak at block: [10] #swap rest at block 10 for eegbreak
    timing:
        block title screen: 1.0             # how long in seconds is the block title screen?
        intertrial interval: 2.0            # how long in seconds is the intertrial interval? (here is where you load stims)
        stimulus presentation window: 4.0   # ***** how long in seconds is the stimulus presentation window?
        prestimulus period: 1.0             # how long in seconds is the prestimulus period
        difficulty cue duration: .5           # how long in seconds is the difficulty cue shown? (ad 2/8/17)
        post stimulus waiting period: 1.0   # how long in seconds is the post stimulus waiting period?
        rest block duration: 30.0            # how long in seconds is the rest block duration?
        stimulus offset buffer: 1.0         #  ***** how longer is seconds is the stimulus offset buffer?
        frames to fade movie: 30            #  *****   how many frames should we fade the movie for?
        fade movie buffer: 1.0              # how long in seconds do you want to devote to fading in the movie?
        answer choice timeout: 5.0       # how long before we timeout the answer choice? #CHANGE BACK TO 5 seconds5
stimuli:
    instructions:
        units: pix
        pos: [0,0]
        height: 40
        color: gray
        font: Arial
        pages:
            - In this experiment you will be asked to identify English words, letter combinations, or environmental sounds. Sometimes you will just hear a word or sound, other times you will see a video of a person saying a word. Space to continue...
            - The items may be difficult to understand. The word Hard at the beginning of the trial means the item will be harder to understand, the word Easy means it will be easier. Listen carefully and try to figure out what you heard. Space to continue...
            - After you listen to the item, you will be given four choices. Use the 4 arrow keys to choose the answer that best matches what you heard. Space to continue...
            - For example, if what you heard matches the answer on the top of the screen, press the up arrow. Space to continue...
            - Please do your best to answer quicly but correctly. It is more important to be accurate than to be fast. Press space to start the experiment...
        rest instructions: You will now be given a 30 second break.  The experiment will resume automatically.
    block title:
        units: pix
        pos: [0,0]
        height: 80
        color: gray
        font: Arial
    difficulty text:
        units: pix
        pos: [0,0]
        height: 80
        color: red
        font: Arial
    fixation cross:
        units: pix
        pos: [0,0]
        height: 80
        color: gray
        font: Arial
    image mask:
        pos: [0, 50]               # what do you want the mask to be?  'gauss' gives gabor; 'circle' gives circular patch
        size: [664, 406]
        units: pix
    movie:
        pos: [0,50]
        size: [720, 400]
    noise:
        sampleRate: 48000
    word:
        sampleRate: 48000
    answers:
        left:
            units: pix
            pos: [-140, 0]
            height: 30
            color: gray
            font: Arial
        right:
            units: pix
            pos: [140, 0]
            height: 30
            color: gray
            font: Arial
        up:
            units: pix
            pos: [0, 140]
            height: 30
            color: gray
            font: Arial
        down:
            units: pix
            pos: [0, -140]
            height: 30
            color: gray
            font: Arial
staircases:
    baseline staircase:
        Auditory:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.95 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Auditory         # the condition we are doing (for marking data)
                startVal: 2.0              # a number; the initial value of the staircase
                stepSizes: 2               # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 6                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Auditory         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Visual:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.90 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Visual         # the condition we are doing (for marking data)
                startVal: 2.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 6                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                 # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Visual         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Environmental:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.90 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Environmental         # the condition we are doing (for marking data)
                startVal: 3.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 6                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Environmental         # the condition we are doing (for marking data)
                startVal: 2.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Phoneme:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.90 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Phoneme         # the condition we are doing (for marking data)
                startVal: 2.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 6                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: baseline         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Phoneme         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 2             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
    main staircase:
        Auditory:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.95 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Auditory         # the condition we are doing (for marking data)
                startVal: 3.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 6                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Auditory         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Visual:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.90 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Visual         # the condition we are doing (for marking data)
                startVal: 2.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 5                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Visual         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Environmental:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.95 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Environmental         # the condition we are doing (for marking data)
                startVal: 4.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 5                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Environmental         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
        Phoneme:
            easy:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.95 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: easy                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Phoneme         # the condition we are doing (for marking data)
                startVal: 4.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 5                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
            hard:
                intensities: 1 # what is this? is this what it wants?
                startValSd: 2 # ad
                pThreshold: 0.35 # ad
                gamma: 0.25 # ad
                staircasename: main         # which staircase we are doing (for marking data)
                label: hard                 # 'easy' or 'hard'; label for which sub-staircase this is
                condition: Phoneme         # the condition we are doing (for marking data)
                startVal: 1.0              # a number; the initial value of the staircase
                stepSizes: 4             # the size of steps (how much intensity to go up per step)
                stepType: db
                nUp: 1                      # the number of 'incorrect' responses before the staircase level increases
                nDown: 2                    # the number of 'correct' responses before the staircase level decreases
                minVal: 0.05                # None or a number; the smallest legal value for the staircase; prevents it from reaching impossible values
                maxVal: None                  # None or a number; The largest legal value for the staircase; prevents it from reaching impossible values
