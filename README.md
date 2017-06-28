== MQTT Occupancy Estimator ==
By combining multiple AXIS People Counters to accumulate people walking in and out an estimation of home occupancy can be made. Using knowledge such as movement (from PIR detectors), interaction with home electronics and locking/unlocking of doors the estimation can be improved.

Currently supported:

* Accumulate MQTT events from one or more cameras to get occupancy estimation
* Reset occupancy estimation (in database and AXIS Occupancy Estimators) using an MQTT command

Todo:
* Implement more sensors and logic
* Clean up settings
* Move passwords to a network vault
* Kill all threads if mqtt-thread segfault, needed to trigger restart of service

== Installation ==
* Move the occupancy.service file to /etc/systemd/system
* Make sure the path in occupancy.service correspons to your python module's path
* Reload and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start occupancy.service
sudo systemctl enable occupancy.service
```
* Show log:
```bash
sudo journalctl -u occupancy -f
```
