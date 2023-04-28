# LO_traps/user/forcing

This page provides an in-depth explanation of how TRAPS get integrated into the model domain.

---
## trapsfun.py

This section describes the helper functions defined in the `trapsfun.py` script. These functions are used to determine where in a model domain TRAPS should be located given their lat/lon coordinates.

### Main Script:

<details><summary><code><strong>traps_placement</strong></code></summary>
---------------------------add description here!!!
</details><br>

### Tiny River Handling

<details><summary><code><strong>get_nearest_coastal_cell_riv</strong></code></summary>
---------------------------add description here!!!
</details><br>

<details><summary><code><strong>get_cell_info_riv</strong></code></summary>

A grid cell of interest is determined in `get_nearest_coatal_cell_riv` before being fed as an input to this function.
This function checks if the grid cell of interest is a coastal water cell. If it is a coastal water cell, then the function returns:
- indices of the coastal grid cell
- distance from the center of the grid cell to the river mouth
- direction of river flow, given the relative position of the nearest land cell

To calculate these values, this function follows the following steps:

1. Checks if the grid cell of interest is a coastal cell by checking whether any adjacent cells have a land mask. The figure below shows a simple domain with a land cell located to the North and East of the grid cell of interest.

<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234992835-2f83a04a-82b2-423a-ae6c-19eff040c75e.png" width="400"/><br></p><br>

2. If the grid cell is indeed coastal, then the distance from the river mouth to the grid cell is recorded as an output. The function then proceeds to steps 3 and 4. If the grid cell is not coastal, then the function ends and nothing is returned.

<p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995892-1907373b-d2ac-4284-82a3-6efb6d121563.png" width="400"/><br></p><br>

3. Then the function needs to decide from which land cell the river should flow (i.e. what direction does the river come from?)<br> First, the function calculates the distance from the river mouth to each adjacent land cell. <br> <p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995894-d6a13d85-23f7-4d08-ba52-d1e881511c8a.png" width="400"/><br></p><br> The river flow direction is set by whichever adjacent land cell is closest to the original river mouth lat/lon coordinates. In our simple example, the Eastern land cell is closest to the river. Thus, the function decides that the river mouth flows westward into the grid cell of interest from the eastern land cell. <br> <p style="text-align:center;"><img src="https://user-images.githubusercontent.com/15829099/234995895-3b0f6e21-c479-4e6c-bde2-c2da72f2d0a2.png" width="400"/><br></p><br>

4. Finally, the function outputs the indices of the coastal grid cell, the distance from the river mouth to the coastal grid cell, and the direction of river flow into the grid cell.
</details><br>

### Point Source Handling

<details><summary><code><strong>get_nearest_coastal_cell_wwtp</strong></code></summary>
---------------------------add description here!!!
</details><br>

<details><summary><code><strong>get_cell_info_wwtp</strong></code></summary>

A grid cell of interest is determined in `get_nearest_coatal_cell_wwtp` before being fed as an input to this function.

This function is the point source equivalent of `get_cell_info_riv`, except it is much simpler. In general, point sources are easier to handle than tiny rivers because point sources can be located on an water cell (including in open water), whereas rivers must be located on a land-adjacent water cell. Thus, this function only needs to check whether the grid cell of interest is a water cell. If so, the function returns the i,j-indices of the grid cell of interest as well as the distance from the center of the grid cell to the point source. If the grid cell of interest is not a water cell, then nothing is returned.
</details>