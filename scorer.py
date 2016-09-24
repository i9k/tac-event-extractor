"""
---------------------------------------------------------------------
Instances of this class will calculate precision, recall and F-score
---------------------------------------------------------------------
inputs: list or list of lists containing the correct event labels
        list or list of lists containing the predicted event labels

outputs:  score dict of dicts of the form {event:{#:12,"TP":3,"FP":0,"FN":92,"PRE","REC","F"}}

Note:
        - True positives are relevant items that we correctly identified as relevant.
        - True negatives are irrelevant items that we correctly identified as irrelevant.
        - False positives (or Type I errors) are irrelevant items that we incorrectly identified as relevant.
        - False negatives (or Type II errors) are relevant items that we incorrectly identified as irrelevant.
        - PRE, which indicates how many of the items that we identified were relevant,
            is TP/(TP+FP).
        - REC, which indicates how many of the relevant items that we identified, is
            TP/(TP+FN).
        - The F1 is the harmonic mean of the PRE and REC (2 × PRE × REC)/(PRE+REC).

          -- from Bird(2009)
"""

from collections import defaultdict

class Scorer(object):

    def __init__(self, correct_labels, predicted_labels):

        self.correct_labels = correct_labels
        self.predicted_labels = predicted_labels
        self.score_dict = defaultdict(lambda: defaultdict(int))

    def _get_scores(self):

        for i, lab in enumerate(self.predicted_labels):

            if self.correct_labels[i] == self.predicted_labels[i]:  # guessed right

                if self.correct_labels[i] == "O":  # but it's non-event
                    pass
                else:  # it's an event
                    for e in self.correct_labels[i].split(","):  # there could be several event labels all predicted correctly
                        self.score_dict[e]["TP"] += 1
                        self.score_dict[e]["#"] += 1  # just counting ocurrences

            else:  # guessed wrong

                if self.correct_labels[i] == "O":  # and it's actually a non-event while we said event
                    for e in self.predicted_labels[i].split(","):  # there could be several event labels
                        self.score_dict[e]["FP"] += 1  # 

                else:  # it's actually some event but we got it wrong: we think either non-event or wrong event or partly right event

                    # suppose we reckon it's non-event
                    if self.predicted_labels[i] == "O":
                        for e in self.correct_labels[i].split(","):  # there could be several event labels
                            self.score_dict[e]["FN"] += 1
                            self.score_dict[e]["#"] += 1 

                    else:  # we think it's an event but a different one (i.e. not all predicted labels are right)
                        
                        clabs = self.correct_labels[i].split(",")
                        for e in clabs:
                            self.score_dict[e]["#"] += 1
                        plabs = self.predicted_labels[i].split(",")

                        for ep in plabs:
                            if ep in clabs:  # this label is among the correct ones
                                self.score_dict[ep]["TP"] += 1
                            else:
                                self.score_dict[ep]["FP"] += 1
                        for cl in clabs:
                            if cl not in plabs:  # some of the correct labels were not predicted
                                self.score_dict[cl]["FN"] += 1

        # now calculate precision, recall and f-score for each event collected in score_dict
     
        for event in self.score_dict:
           # to calculate precision, we need TP+FP>0
           try:
               self.score_dict[event]["PRE"] = round(self.score_dict[event]["TP"]/(self.score_dict[event]["TP"] + self.score_dict[event]["FP"]),2)
           except ZeroDivisionError:
               self.score_dict[event]["PRE"] = float('nan')
           # to calculate recall we need TP+FN>0
           try:
               self.score_dict[event]["REC"] = round(self.score_dict[event]["TP"]/(self.score_dict[event]["TP"] + self.score_dict[event]["FN"]),2)
           except ZeroDivisionError:
               self.score_dict[event]["REC"] = float('nan')

           # to calculate f-score, we need both precision and recall be nonzero; 
           
           if self.score_dict[event]["PRE"]*self.score_dict[event]["REC"] > 0:
                self.score_dict[event]["F"] = 1/self.score_dict[event]["PRE"] + 1/self.score_dict[event]["REC"]
           else:
                self.score_dict[event]["F"] = float('nan')
        
        return self.score_dict