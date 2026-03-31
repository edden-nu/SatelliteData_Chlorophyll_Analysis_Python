import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import netCDF4 as nc
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from matplotlib.lines import Line2D

# =========================
# 1. Read NetCDF file
# =========================
filename = 'Chla_20220724_8days.nc'
dataset = nc.Dataset(filename)
print(dataset)

chla = np.squeeze(dataset.variables['chlor_a'][:])
lat = dataset.variables['latitude'][:]
lon = dataset.variables['longitude'][:]

# If masked array -> convert masked values to np.nan
if np.ma.isMaskedArray(chla):
    chla = chla.filled(np.nan)

# =========================
# 2. City coordinates
# =========================
city_coordinates = {
    'Xiamen':   (24.7980, 118.0894),
    'Taipei':   (25.0330, 121.5654),
    'Wenzhou':  (27.7809, 120.39584),
    'Fuzhou':   (26.2681, 119.1952),
    'Quanzhou': (24.9999, 118.5200),
    'Putian':   (25.4392, 118.8000)
}

city_colors = {
    'Xiamen': 'red',
    'Taipei': 'blue',
    'Wenzhou': 'green',
    'Fuzhou': 'purple',
    'Quanzhou': 'orange',
    'Putian': 'brown'
}

# =========================
# 3. Core function
# Find nearest valid 5x5 window mean
# Condition:
# - 5x5 window must have at least 13 valid cells
# - mean ignores NaN
# - choose the nearest valid center to the city
# =========================
def find_nearest_valid_5x5_mean(lat, lon, chla, lat_city, lon_city, search_radius=15, min_valid_count=13):
    """
    Search around the city for the nearest candidate center point.
    For each candidate center, take a 5x5 window.
    Accept only if valid (non-NaN) cells >= min_valid_count.
    Compute mean over valid cells only.
    
    Returns:
        best_lat, best_lon, best_mean, best_count
    """

    # nearest raw grid index to city
    lat_idx_center = np.abs(lat - lat_city).argmin()
    lon_idx_center = np.abs(lon - lon_city).argmin()

    best_dist = np.inf
    best_lat = None
    best_lon = None
    best_mean = np.nan
    best_count = 0

    i_start = max(0, lat_idx_center - search_radius)
    i_end   = min(len(lat), lat_idx_center + search_radius + 1)
    j_start = max(0, lon_idx_center - search_radius)
    j_end   = min(len(lon), lon_idx_center + search_radius + 1)

    for i in range(i_start, i_end):
        for j in range(j_start, j_end):

            # 5x5 window centered at (i, j)
            r0 = max(0, i - 2)
            r1 = min(len(lat), i + 3)
            c0 = max(0, j - 2)
            c1 = min(len(lon), j + 3)

            window = chla[r0:r1, c0:c1]
            valid_values = window[~np.isnan(window)]

            # must have more than half valid cells in 5x5
            if valid_values.size < min_valid_count:
                continue

            window_mean = np.mean(valid_values)

            # straight-line distance in lat/lon space
            dist = np.sqrt((lat[i] - lat_city) ** 2 + (lon[j] - lon_city) ** 2)

            if dist < best_dist:
                best_dist = dist
                best_lat = float(lat[i])
                best_lon = float(lon[j])
                best_mean = float(window_mean)
                best_count = int(valid_values.size)

    return best_lat, best_lon, best_mean, best_count

# =========================
# 4. Plot map
# (keep your original style)
# =========================
lat0, lat1, lon0, lon1 = lat.min(), lat.max(), lon.min(), lon.max()

fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.add_feature(cfeat.LAND, facecolor='white', edgecolor='black')
ax.set_extent((lon0, lon1, lat0, lat1))

img = ax.pcolormesh(lon, lat, chla[:, :], shading='auto')
cbar = plt.colorbar(img, ticks=[2, 4, 6, 8, 10, 12])
cbar.set_label('Chlorophyll Concentration', rotation=270, labelpad=15)

ax.set_title('Chlorophyll Concentration 8 days average')
ax.set_xticks([118, 120, 122, 124, 126])
ax.set_yticks([20, 22, 24, 26, 28])

legend_elements = []
results = []

# =========================
# 5. Process each city
# =========================
for city, (lat_city, lon_city) in city_coordinates.items():
    nearest_lat, nearest_lon, chla_mean, valid_count = find_nearest_valid_5x5_mean(
        lat, lon, chla, lat_city, lon_city,
        search_radius=15,
        min_valid_count=13
    )

    color = city_colors[city]

    print(f'{city}:')
    print(f'  city = ({lat_city}, {lon_city})')
    print(f'  nearest valid center = ({nearest_lat}, {nearest_lon})')
    print(f'  5x5 mean chlorophyll = {chla_mean}')
    print(f'  valid cell count in 5x5 = {valid_count}')
    print('------------------')

    results.append({
        'City': city,
        'City_Lat': lat_city,
        'City_Lon': lon_city,
        'Center_Lat': nearest_lat,
        'Center_Lon': nearest_lon,
        'Mean_Chla_5x5': chla_mean,
        'Valid_Count_5x5': valid_count
    })

    # city point
    ax.plot(lon_city, lat_city,
            marker='o', color=color, markersize=6,
            transform=ccrs.PlateCarree())

    # nearest valid sampling center
    if nearest_lat is not None and nearest_lon is not None:
        ax.plot(nearest_lon, nearest_lat,
                marker='o', color='black', markersize=3,
                transform=ccrs.PlateCarree())

        ax.plot([lon_city, nearest_lon],
                [lat_city, nearest_lat],
                'k--', linewidth=0.5,
                transform=ccrs.PlateCarree())

    legend_elements.append(
        Line2D([0], [0],
               marker='o', color='w',
               markerfacecolor=color, markersize=8,
               label=city)
    )

legend_elements.append(
    Line2D([0], [0],
           marker='o', color='w',
           markerfacecolor='black', markersize=6,
           label='Nearest valid 5x5 center')
)

# legend inside lower-right corner
ax.legend(handles=legend_elements,
          loc='lower right',
          title='City legend',
          frameon=True,
          facecolor='white',
          framealpha=0.8)

plt.tight_layout()
plt.show()
