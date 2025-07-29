## algorithm for dates handling

Problem: Poznan ZTM API sends data for future days that overrides previous schedules, for example:

![alt text](image.png)

Here we can see that on 04.07 came file that applies from 07.07 - so I have to save it for the future, without deleting current schedule, and switch to it when time for that comes.

Additionally, file 20250707_20250731.zip overrides the old file, that also ends on 31.07. So I should rearrange dates that this old schedule applies to. 

Here's my little algorithm for that:

1. first file has date from 01.07 to 31.07
2. save file `20250701-20250731.db`
3. new file comes - from 04.07 to 31.07
4. search files that override this range: `old_end_date > new_start_date` (in this case - `31.07 > 04.07 -> TRUE`)
5. change old file's name to `[start_date]-[new_start_date - 1].db`
6. save new file: `[new_start_date]-[new_end_date].db`
7. repeat steps 4-6 for every new file

Basing on historical ZTM data, there are no situations that are not handled by this workflow (for example, new file end date smaller that old file end date, and old file's schedule applying after end date of the new one)

## TODOs

- Add databases deletion after some time
- Make http server and thread that runs fetch once a day
- make esp client in micropython