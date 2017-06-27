By combining multiple AXIS People Counters to accumulate people walking in and out an estimation of home occupancy can be made. Using knowledge such as movement (from PIR detectors), interaction with home electronics and locking/unlocking of doors the estimation can be improved.

Currently supported:

* Accumulate MQTT events from one or more cameras to get occupancy estimation
* Reset occupancy estimation (in database and AXIS Occupancy Estimators) using an MQTT command

Todo:
* Implement more sensors and logic
* Fix a unitfile which starts module without a start shell script file
* Improve the journal logging
* Clean up settings
* Move passwords to a network vault
