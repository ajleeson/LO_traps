# LO_traps/user/forcing

This page provides an in-depth explanation of how functions integrate TRAPS into the model domain.

---
## make_forcing_main.py

<!-- This script is based off of Parker MacCready's make_forcing_main.py script used in LiveOcean. I have modified it to incoroporate TRAPS. This README only describes portions of the script that are relevant to the addition of TRAPS. -->

------- Work in progress. Check back later for updates -------

---
## trapsfun.py

This section describes the helper functions defined in the `trapsfun.py` script. These functions determine where in a model domain TRAPS should be located given their lat/lon coordinates.

### Main Script: `traps_placement`

<details><summary><strong>Summary</strong></summary>
This is the main function that places TRAPS in the model domain. The script make_forcing_main calls traps_placement, twice: once with an input of 'riv' for tiny rivers, and a second time with an input of 'wwtp' for point sources. The script reads lat/lon coordinates of TRAPS in LO_data/traps/SSM_source_info.xlsx, then decides where to place the TRAPS in the model domain.

This function does not output anything, but it does save .csv files with TRAPS location indices in LO_data/grids/[gridname]. In the same folder, this function also saves figures depicting the location of the placed TRAPS.

The following subsections provide more details about the placement algorithm and plotting script.

</details>

<details><summary><strong>Algorithm</strong></summary>

*Tiny Rivers*

1. For each river listed in SSM_source_info.xlsx, this function first checks if the river is already pre-existing in LiveOcean. If it is pre-existing, then this function does nothing and skips to the next river. If the river is not pre-existing in LiveOcean, then this function proceeds to the next step.
2. Several larger rivers in the SSM discharge to two grid cells. This script consolidates these rivers to discharge from just one grid cell. To do so, the function checks whether the river name has the format '[rivername] -1' or '[rivername] -2', indicating that it is a two-cell river. If so, then the function averages the lat/lon coordinates of '[rivername] -1' and '[rivername] -2' to obtain a single set of lat/lon coordinates.
3. This function then feeds the lat/lon coordinates of each river ainto `get_nearest_coastal_cell_riv` to obtain i,j-indices and direction of the placed river (See the "Tiny River Handling" section below for more details).
4. Finally, this function saves river information in LO_data/grids/[gridname]/triv_info.csv.

*Point Sources*

There are no pre-existing rivers in LiveOcean, nor are there any point sources that discharge to multiple grid cells in the SSM. Thus, point sources are easier to handle than tiny rivers.

1. First, the functions feeds each point source listed in SSM_source_info.xlsx into `get_nearest_coastal_cell_wwtp` to obtain the i,j-indices of the places source (See the "Point Source Handling" section below for more details).
2. Then, this function saves point source information in LO_data/grids/[gridname]/wwtp_info.csv.

</details>

<details><summary><strong>Plotting</strong></summary>
------- Work in progress. Check back later for updates -------
</details><br>

### Tiny River Handling

<details><summary><code><strong>get_nearest_coastal_cell_riv</strong></code></summary>
This function finds the closest coastal grid cell to a river mouth, then returns:

- indices of nearest coatal grid cell to river mouth
- river direction
- number of "rings" away the nearest coastal cell is from the river mouth

To calculate these values, this function follows the following steps:

1. Given river mouth lat/lon coordinates, the algorithm determines in which grid cell the river mouth is originally located in.<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235255958-37e851f5-820e-4b53-aeca-85c101b7ddc8.png" width="500"/><br></p>

2. Checks whether the starting grid cell is a coastal cell by calling `get_cell_info_riv`. If the starting grid cell is a coastal grid cell, then the function returns the i,j-indices of the cell as well as river direction.

3. If the starting grid cell is not a coastal cell, then the function begins searching in a ring around the starting grid cell. For each cell in the surrouding ring, the function calls `get_cell_info_riv`. If no coastal grid cells are found in the first ring, then the function begins searching the next ring, and so on and so forth until a coastal cell is found.<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235255959-fb10f648-0d58-4647-a8d0-2ae20e1bbb0b.png" width="500"/><br></p>

4. If one coastal cell is found in a ring, then the function records the coastal cell i,j-indices, the distance from the coastal cell to the river mouth, and the river direction (which are outputs of `get_cell_info_riv`).<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235255962-fca53e68-2195-4d97-a66c-48962d2d491e.png" width="500"/><br></p>If more than one coastal cell is found in a ring, then information will be recorded for the coastal cell that is nearest to the river mouth.<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235255966-a26a7d8b-b8b6-41b7-a134-3333a43241ef.png" width="500"/><br></p><br>

Note that this function always checks for a "nearest coastal cell" one ring further out than the first coastal cell-containing ring. This check is important for stretched grids. In a stretched grid, it is possible that the nearest coastal grid cell is located several rings away, even if there are coastal grid cells in closer rings.

<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235260467-dc0a89b9-5a26-48e5-914e-dd0a87c043da.png" width="450"/><br></p>

</details>

<details><summary><code><strong>get_cell_info_riv</strong></code></summary>

A grid cell of interest is determined in `get_nearest_coatal_cell_riv` before being fed as an input to this function.
This function checks if the grid cell of interest is a coastal water cell. If it is a coastal water cell, then the function returns:

- indices of the coastal grid cell
- distance from the center of the grid cell to the river mouth
- direction of river flow, given the relative position of the nearest land cell

To calculate these values, this function follows the following steps:

1. Checks if the grid cell of interest is a coastal cell by checking whether any adjacent cells have a land mask. The figure below shows a simple domain with a land cell located to the North and East of the grid cell of interest.<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234992835-2f83a04a-82b2-423a-ae6c-19eff040c75e.png" width="400"/><br></p>

2. If the grid cell is indeed coastal, then the distance from the river mouth to the grid cell is recorded as an output. The function then proceeds to steps 3 and 4. If the grid cell is not coastal, then the function ends and nothing is returned.<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995892-1907373b-d2ac-4284-82a3-6efb6d121563.png" width="400"/><br></p>

3. Then the function needs to decide from which land cell the river should flow (i.e. what direction does the river come from?)<br> First, the function calculates the distance from the river mouth to each adjacent land cell. <br> <p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995894-d6a13d85-23f7-4d08-ba52-d1e881511c8a.png" width="400"/><br></p> The river flow direction is set by whichever adjacent land cell is closest to the original river mouth lat/lon coordinates. In our simple example, the Eastern land cell is closest to the river. Thus, the function decides that the river mouth flows westward into the grid cell of interest from the eastern land cell. <br> <p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995895-3b0f6e21-c479-4e6c-bde2-c2da72f2d0a2.png" width="400"/><br></p>

4. Finally, the function outputs the indices of the coastal grid cell, the distance from the river mouth to the coastal grid cell, and the direction of river flow into the grid cell.

</details><br>

### Point Source Handling

<details><summary><code><strong>get_nearest_coastal_cell_wwtp</strong></code></summary>

This function is the point source equivalent of `get_nearest_coastal_cell_riv`. The main difference is that this function calls `get_cell_info_wwtp` rather than `get_cell_info_riv`.

The nearest coastal cell that this function is searching for is *any* water cell. This function does not search through rings if the starting grid cell is already a water cell.

This function only needs to search for the nearest coastal grid cell if the starting cell is a land cell.

<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/235257876-aedcee38-b4b1-4899-a40f-bce06cb7c6ed.png" width="800"/><br></p>

</details>

<details><summary><code><strong>get_cell_info_wwtp</strong></code></summary>

A grid cell of interest is determined in `get_nearest_coatal_cell_wwtp` before being fed as an input to this function.

This function is the point source equivalent of `get_cell_info_riv`, except it is much simpler. In general, point sources are easier to handle than tiny rivers because point sources can be located on an water cell (including in open water), whereas rivers must be located on a land-adjacent water cell. Furthermore, rivers need an associated flow direction, but point sources do not. Thus, this function only needs to check whether the grid cell of interest is a water cell. If so, the function returns the i,j-indices of the grid cell of interest as well as the distance from the center of the grid cell to the point source. If the grid cell of interest is not a water cell, then nothing is returned.
</details><br>

### Other Helper Functions

------- Work in progress. Check back later for updates -------

<!-- <details><summary><code><strong>in_domain</strong></code></summary>
-----------------------description!
</details>

<details><summary><code><strong>cell_in_domain</strong></code></summary>
-----------------------description!
</details>

<details><summary><code><strong>get_qt_bio</strong></code></summary>
-----------------------description!
</details>

<details><summary><code><strong>combine_adjacent</strong></code></summary>
-----------------------description!
</details>

<details><summary><code><strong>weighted_average</strong></code></summary>
-----------------------description!
</details>

<details><summary><code><strong>LO2SSM_name</strong></code></summary>
-----------------------description!
</details> -->