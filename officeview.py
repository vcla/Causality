# dict keys are frame numbers
# frames are only reported when a fluent changes, and only for the fluent(s) that changed; fluents are considered to be on or off ("light" is treated as "light_on", and then "light_off" is calculated from that internally, for instance)

import causal_grammar

fluent_parses, temporal_parses = causal_grammar.import_xml("officeview3.xml")
#import causal_grammar_office as causal_forest # sets up causal_forest
import causal_grammar_office_bigger as causal_forest # sets up causal_forest
causal_grammar.process_events_and_fluents(causal_forest.causal_forest, fluent_parses, temporal_parses, causal_grammar.kFluentThresholdOnEnergy, causal_grammar.kFluentThresholdOffEnergy, causal_grammar.kReportingThresholdEnergy)
