// Version 10.0

//var aoi = table.geometry();

//var mean_smooth = 2000
var kernel_smooth = 2000
var aoi = geometry
// Select DOI search interval
var startdate = "2022-02-21"
var enddate = "2022-02-26"

// Select snow cover index search interval month
//var SC_startdate = "2022-02"


var SC_startdate = startdate.slice(0,7)+"-01"
var SC_enddate = startdate.slice(0,7)+"-28"

print(SC_startdate)

// Defining names of output files
var subtract_autumn_VHname = startdate.slice(0,10)+"VHyr2k"
var subtract_autumn_VVname = startdate.slice(0,10)+"VV"
var subtract_autumn_CSname = startdate.slice(0,10)+"CSyr2k"
var subtract_autumn_CRname = startdate.slice(0,10)+"CRyr2k"
var subtract_CSname = startdate.slice(0,10)+"CS_date"

var autumnsubtractname = startdate.slice(0,10)+"-CS5G"
var springsubtractname = startdate.slice(0,10)+"-CR10G"
var autumnsubtractname = startdate.slice(0,10)+"-CS5G"
var VHname = startdate.slice(0,10)+"VH"
var rationame = startdate.slice(0,10)+"Ratio"
var subtractname = startdate.slice(0,10)+"Subtract"
var binarymaskname = startdate.slice(0,10)+"Binary_Mask500m"
var springdiffdividename = startdate.slice(0,10)+"Dec_diffratio"
var autumndiffdividename = startdate.slice(0,10)+"Autumn_diffratio"
var springrationame = startdate.slice(0,10)+"Spring_ratio"
var autumnrationame = startdate.slice(0,10)+"Autumn_ratio"

// Import AOI from GEE Assets and get geometry
// var aoi = table2.geometry();

// Import Sentinel-1 Collection - Filter dates so that the start-date is the date you are interested in
var s1 =  ee.ImageCollection('COPERNICUS/S1_GRD')
			.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) // Retrieve the VH band
			.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) // Retrieve the VV band
			.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING')) // Use Descending orbit as it passes over AOI 6 am
			.filter(ee.Filter.eq('instrumentMode', 'IW')) // Select Wide-Swath
			.filter(ee.Filter.eq('relativeOrbitNumber_start', 110)) // Selection of orbit number, to get images with similar viewing angle
      //.filter(ee.Filter.eq('sliceNumber', 9)) // Select slice number to get image that covers whole aoi
			.filterBounds(aoi)
			//.filterBounds(aoi) // Filter within aoi
			.filterDate(startdate,enddate); // Filter date - set start-date to wanted date!
print(s1,'s1')

// Import Sentinel-1 Collection (SPRING selection)
var s1_spring =  ee.ImageCollection('COPERNICUS/S1_GRD')
			.filter([
			ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'), // Retrieve the VH band
			ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'), // Retrieve the VV band
			ee.Filter.eq('orbitProperties_pass', 'DESCENDING'), // Use Descending orbit as it passes over AOI 6 am
			ee.Filter.eq('instrumentMode', 'IW'), // Select Wide-Swath
			ee.Filter.eq('relativeOrbitNumber_start', 110), // Selection of orbit number, to get images with similar viewing angle
      //ee.Filter.eq('sliceNumber', 9),// Select slice number to get image that covers whole aoi
			]).filterBounds(aoi)
			//.filterBounds(aoi) // Filter within aoi
			.filterDate("2017-12-01","2019-12-05"); // Filter date - set start-date to wanted date!

// Import Sentinel-1 Collection (AUTUMN selection)
var s1_autumn =  ee.ImageCollection('COPERNICUS/S1_GRD')
			.filter([
			ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'), // Retrieve the VH band
			ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'), // Retrieve the VV band
			ee.Filter.eq('orbitProperties_pass', 'DESCENDING'), // Use Descending orbit as it passes over AOI 6 am
			ee.Filter.eq('instrumentMode', 'IW'), // Select Wide-Swath
			ee.Filter.eq('relativeOrbitNumber_start', 110), // Selection of orbit number, to get images with similar viewing angle
      //ee.Filter.eq('sliceNumber', 9),// Select slice number to get image that covers whole aoi
			]).filterBounds(aoi)
			//.filterBounds(aoi) // Filter within aoi
			.filterDate("2020-01-01","2020-12-30"); // Filter date - set start-date to wanted date!

print(s1_autumn,'s1_autumn')
// Apply Terrain Correction to Image Collection using the 'map' functiond
var s1_terrain = s1.map(terrainCorrection);
var s1_terrain_spring = s1_spring.map(terrainCorrection);
var s1_terrain_autumn = s1_autumn.map(terrainCorrection);

// Apply the Refined-Lee Speckle Filter to the Image Collection
var s1_DOI = s1_terrain.map(refinedLee);
var s1_DOI_spring = s1_terrain_spring.map(refinedLee);
var s1_DOI_autumn = s1_terrain_autumn.map(refinedLee);


//var s1_DOI = s1_DOI.map(dbToPower);
//var s1_DOI_spring = s1_DOI_spring.map(dbToPower);
//var s1_DOI_autumn = s1_DOI_autumn.map(dbToPower);
//-----------------------------------------------MASKING------------------------------------------------------------

// Apply function for masking out wet snow
var s1_wetsnowmasked = s1_DOI.map(wetsnowmask_function);
var s1_wetsnowmasked_spring = s1_DOI_spring.map(wetsnowmask_function);
var s1_wetsnowmasked_autumn = s1_DOI_autumn.map(wetsnowmask_function);


Map.addLayer(s1_wetsnowmasked,{min:-25,max:20},"WSM");

// Apply function for selecting areas with snow
var s1_snowcover = s1_wetsnowmasked.map(snowcovermask_function)
var s1_snowcover_spring = s1_wetsnowmasked_spring.map(snowcovermask_function)
var s1_snowcover_autumn = s1_wetsnowmasked_autumn.map(snowcovermask_function)


// Apply function for masking out low elevation
var s1_DEM_masked = s1_snowcover.map(DEM_function);
var s1_DEM_masked_spring = s1_snowcover_spring.map(DEM_function);
var s1_DEM_masked_autumn = s1_snowcover_autumn.map(DEM_function);

// Apply function for masking out forest, permasnow and water
var s1_masked = s1_DEM_masked.map(landcovermask_function);
var s1_masked_spring = s1_DEM_masked_spring.map(landcovermask_function);
var s1_masked_autumn = s1_DEM_masked_autumn.map(landcovermask_function);

//---------------------------------------------RESAMPLING AND MOSAICING-----------------------------------------------


// Resample
//var s1_resampled = s1_masked.map(resampling_function);
//var s1_resampled_spring = s1_masked_spring.map(resampling_function);
//var s1_resampled_autumn = s1_masked_autumn.map(resampling_function);

// Mosaic
var s1_mosaiced = mosaicing_function(s1_masked);
var s1_spring_min = ee.Image(s1_masked_spring.min());
var s1_autumn_median = ee.Image(s1_masked_autumn.mean());

var Angle = s1_mosaiced.select(['angle'])

var Binary_Mask = s1_mosaiced.gt(-999);
var Binary_Mask = Binary_Mask.updateMask(Binary_Mask);


//-----------------------------------------------SMOOTHING AND REMASKING----------------------------------------------

// Apply function for smoothing image
var s1_smoothed = smoothing_function(s1_mosaiced);
var s1_smoothed_spring = smoothing_function(s1_spring_min);
var s1_smoothed_autumn = smoothing_function(s1_autumn_median);

var s1_smoothed_masked = s1_smoothed.updateMask(Binary_Mask);
var s1_smoothed_masked_spring = s1_smoothed_spring.updateMask(Binary_Mask);
var s1_smoothed_masked_autumn = s1_smoothed_autumn.updateMask(Binary_Mask);

//var s1_smoothed_masked_autumn = s1_smoothed_autumn
//var s1_smoothed_masked_spring = s1_smoothed_spring
//var s1_smoothed_masked = s1_smoothed

//var s1_smoothed_masked = powerToDb(s1_smoothed_masked);
//var s1_smoothed_masked_spring = powerToDb(s1_smoothed_masked_spring);
//var s1_smoothed_masked_autumn = powerToDb(s1_smoothed_masked_autumn); 

//-------------------------------------------DERIVED VARIABLE CALCULATION---------------------------------------------

//test 
//var VH = s1_smoothed_masked_autumn.select(['VV'])

// VH variable
var VH = s1_smoothed_masked.select(['VH'])

// Local Subtract variable
var VV = s1_smoothed_masked.select(['VV'])
var subtract = VH.subtract(VV);
// Local Ratio variable
var ratio = VH.divide(VV);

// VH (autumn) VAR 1
var VH_autumn = s1_smoothed_masked_autumn.select(['VH'])
var subtract_autumn_VH = VH.subtract(VH_autumn);

// VV (autumn) VAR 2
var VV_autumn = s1_smoothed_masked_autumn.select(['VV'])
var subtract_autumn_VV = VV.subtract(VV_autumn);

// Subtract (autumn) VAR 3
var subtract_autumn = VH_autumn.subtract(VV_autumn);
var subtract_autumn_CS = subtract.subtract(subtract_autumn);

// Ratio (autumn) VAR 4
var ratio_autumn = VH_autumn.divide(VV_autumn);
var subtract_autumn_CR = ratio.subtract(ratio_autumn);


Map.addLayer(subtract_autumn_CS,{min:-3,max:7},"subtract_autumn_CS");

// Binary_Mask
Map.addLayer(Binary_Mask,{min:0,max:1},"Binary_Mask");

//-------------------------------------------EXPORT VARIABLES---------------------------------------------

// Forest export
Export.image.toDrive({
  image: forest,
 description: 'forest',
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '4000000000'
 });

// Binary_Mask export
Export.image.toDrive({
  image: Binary_Mask,
 description: binarymaskname,
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '4000000000'
 });

// VH export
Export.image.toDrive({
  image: subtract_autumn_VH,
 description: subtract_autumn_VHname,
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '400000000'
 });

// VV export
Export.image.toDrive({
  image: subtract_autumn_VV,
 description: subtract_autumn_VVname,
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '400000000'
 });

// CS export
Export.image.toDrive({
  image: subtract_autumn_CS,
 description: subtract_autumn_CSname,
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '400000000'
 });

// CR export 
Export.image.toDrive({
  image: subtract_autumn_CR,
 description: subtract_autumn_CRname,
 scale: 500,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '400000000'
 });
 
// Sub export 
Export.image.toDrive({
  image: subtract,
 description: subtract_CSname,
 scale: 100,
 crs: 'EPSG:25833',
 region: aoi,
 //folder: 'RADAR_folder',
 fileFormat: 'GeoTIFF',
 maxPixels: '400000000'
 });



//-------------------------------------------ALL FUNCTIONS---------------------------------------------

// Function for mosaicing list of images
function mosaicing_function(imagelist) {
  var mosaiced = imagelist.mosaic();
  return mosaiced;
}

// Function for resampling
function resampling_function(image) {
  //var crs = 'EPSG:32632';
  var crs = 'EPSG:25833';
  var scale = 10;
  var image = image.resample('bilinear').reproject({crs:crs, scale:scale});
  return image;
}

// Function for smoothing
function smoothing_function(image) {
  var smoothing_radius = mean_smooth;
  var image = image.focal_mean(smoothing_radius, 'circle', 'meters', 1);
  // Define a boxcar or low-pass kernel.
  //var boxcar = ee.Kernel.circle({radius: kernel_smooth, units: 'pixels', magnitude: 1, normalize: true});
  //var image = image.focalMean({kernel:boxcar});
  return image;
}

// Function for creating wet snow mask
function wetsnowmask_function(image) {
  var VH = image.select(['VH']);
  var wetsnow = VH.gt(-30);
  var image = image.updateMask(wetsnow);
  
  return image;
}

function DEM_function(image) {
  var srtm = ee.Image('NASA/NASADEM_HGT/001').clip(aoi);
  //var srtm = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic').clip(aoi);
  var srtm = srtm.select('elevation');
  var DEM = srtm.gt(1000);
  var image = image.updateMask(DEM);
  return image;
}


// Function for creating masks for forest, permanent snow and permanent water
function landcovermask_function(image) {
  var LC_dataset = ee.Image("COPERNICUS/Landcover/100m/Proba-V-C3/Global/2019").select('discrete_classification').clip(aoi)
  // Forest mask
  var forest = LC_dataset.gte(110).and(LC_dataset.lte(126)); // Define forest class
  var forest_buffer = 1500; // Define forest buffer radius
  var forest = forest.focal_max(forest_buffer, 'circle', 'meters'); // Apply buffer to forest class
  var forest = forest.eq(0); // Choose everything but forest
  var image = image.updateMask(forest); // Apply mask to image
  // Permanent water mask
  var water = LC_dataset.eq(80).or(LC_dataset.eq(200)); // Define water class
  var water_buffer = 150; // Define water buffer radius
  var water = water.focal_max(water_buffer, 'circle', 'meters'); // Apply buffer to water class
  var water = water.eq(0); // Choose everything but water
  var image = image.updateMask(water); // Apply mask to image
  // Permanent snow mask
  var permasnow = LC_dataset.eq(70); // Define permanent snow class
  var permasnow_buffer = 150; // Define permasnow buffer radius
  var permasnow = permasnow.focal_max(permasnow_buffer, 'circle', 'meters'); // Apply buffer to permasnow class
  var permasnow = permasnow.eq(0); // Choose everything but permasnow
  var image = image.updateMask(permasnow); // Apply mask to image
  return image, forest;
}

// Function for creating mask for snow cover
function snowcovermask_function(image) {
  var SC_dataset = ee.ImageCollection('MODIS/006/MOD10A1').filter(ee.Filter.date(SC_startdate, SC_enddate));
  var snowcover = SC_dataset.select('NDSI_Snow_Cover').mean();
  var snowcover = snowcover.gt(25);
  var image = image.updateMask(snowcover); // Apply mask to image
  return image;
}


// Terrain correction and Advanced Refined Lee filter // 

/*Copyright (c) 2021 SERVIR-Mekong
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of the data and associated documentation files, to deal in the data
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies, and to permit persons
to whom the data is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
 
THE DATA IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.*/

// Algorithm adapted from https://groups.google.com/g/google-earth-engine-developers/c/ExepnAmP-hQ/m/7e5DnjXXAQAJ

// Implementation by Andreas Vollrath (ESA), inspired by Johannes Reiche (Wageningen)
function terrainCorrection(image) { 
  var imgGeom = image.geometry();
  //var srtm = ee.Image('NASA/NASADEM_HGT/001').clip(imgGeom); // 30m srtm 
  var srtm = ee.Image("UMN/PGC/ArcticDEM/V3/2m_mosaic")
  var sigma0Pow = ee.Image.constant(10).pow(image.divide(10.0));

  // Article ( numbers relate to chapters) 
  // 2.1.1 Radar geometry 
  var theta_i = image.select('angle');
  var phi_i = ee.Terrain.aspect(theta_i)
    .reduceRegion(ee.Reducer.mean(), theta_i.get('system:footprint'), 1000)
    .get('aspect');

  // 2.1.2 Terrain geometry
  var alpha_s = ee.Terrain.slope(srtm).select('slope');
  var phi_s = ee.Terrain.aspect(srtm).select('aspect');

  // 2.1.3 Model geometry
  // reduce to 3 angle
  var phi_r = ee.Image.constant(phi_i).subtract(phi_s);

  // convert all to radians
  var phi_rRad = phi_r.multiply(Math.PI / 180);
  var alpha_sRad = alpha_s.multiply(Math.PI / 180);
  var theta_iRad = theta_i.multiply(Math.PI / 180);
  var ninetyRad = ee.Image.constant(90).multiply(Math.PI / 180);

  // slope steepness in range (eq. 2)
  var alpha_r = (alpha_sRad.tan().multiply(phi_rRad.cos())).atan();

  // slope steepness in azimuth (eq 3)
  var alpha_az = (alpha_sRad.tan().multiply(phi_rRad.sin())).atan();

  // local incidence angle (eq. 4)
  var theta_lia = (alpha_az.cos().multiply((theta_iRad.subtract(alpha_r)).cos())).acos();
  var theta_liaDeg = theta_lia.multiply(180 / Math.PI);
  // 2.2 
  // Gamma_nought_flat
  var gamma0 = sigma0Pow.divide(theta_iRad.cos());
  var gamma0dB = ee.Image.constant(10).multiply(gamma0.log10());
  var ratio_1 = gamma0dB.select('VV').subtract(gamma0dB.select('VH'));

  // Volumetric Model
  var nominator = (ninetyRad.subtract(theta_iRad).add(alpha_r)).tan();
  var denominator = (ninetyRad.subtract(theta_iRad)).tan();
  var volModel = (nominator.divide(denominator)).abs();

  // apply model
  var gamma0_Volume = gamma0.divide(volModel);
  var gamma0_VolumeDB = ee.Image.constant(10).multiply(gamma0_Volume.log10());

  // we add a layover/shadow maskto the original implmentation
  // layover, where slope > radar viewing angle 
  var alpha_rDeg = alpha_r.multiply(180 / Math.PI);
  var layover = alpha_rDeg.lt(theta_i);

  // shadow where LIA > 90
  var shadow = theta_liaDeg.lt(85);

  // calculate the ratio for RGB vis
  var ratio = gamma0_VolumeDB.select('VV').subtract(gamma0_VolumeDB.select('VH'));

  var output = gamma0_VolumeDB.addBands(ratio).addBands(alpha_r).addBands(phi_s).addBands(theta_iRad)
    .addBands(layover).addBands(shadow).addBands(gamma0dB).addBands(ratio_1);

  return image.addBands(
    output.select(['VV', 'VH'], ['VV', 'VH']).set({'system:time_start': image.get('segmentStartTime')}),
    null,
    true
  );
}

function powerToDb(img){
  return ee.Image(10).multiply(img.log10());
}

function dbToPower(img){
  return ee.Image(10).pow(img.divide(10));
}

// The RL speckle filter
function refinedLee(image) {
  
  var bandNames = image.bandNames();
  image = dbToPower(image);
  var result = ee.ImageCollection(bandNames.map(function(b){
    var img = image.select([b]);
    //var copy = image.select([b]).copyProperties(image)

    
    // img must be in natural units, i.e. not in dB!
    // Set up 3x3 kernels 
    var weights3 = ee.List.repeat(ee.List.repeat(1,3),3);
    var kernel3 = ee.Kernel.fixed(3,3, weights3, 1, 1, false);
  
    var mean3 = img.reduceNeighborhood(ee.Reducer.mean(), kernel3);
    var variance3 = img.reduceNeighborhood(ee.Reducer.variance(), kernel3);
  
    // Use a sample of the 3x3 windows inside a 7x7 windows to determine gradients and directions
    var sample_weights = ee.List([[0,0,0,0,0,0,0], [0,1,0,1,0,1,0],[0,0,0,0,0,0,0], [0,1,0,1,0,1,0], [0,0,0,0,0,0,0], [0,1,0,1,0,1,0],[0,0,0,0,0,0,0]]);
  
    var sample_kernel = ee.Kernel.fixed(7,7, sample_weights, 3,3, false);
  
    // Calculate mean and variance for the sampled windows and store as 9 bands
    var sample_mean = mean3.neighborhoodToBands(sample_kernel); 
    var sample_var = variance3.neighborhoodToBands(sample_kernel);
  
    // Determine the 4 gradients for the sampled windows
    var gradients = sample_mean.select(1).subtract(sample_mean.select(7)).abs();
    gradients = gradients.addBands(sample_mean.select(6).subtract(sample_mean.select(2)).abs());
    gradients = gradients.addBands(sample_mean.select(3).subtract(sample_mean.select(5)).abs());
    gradients = gradients.addBands(sample_mean.select(0).subtract(sample_mean.select(8)).abs());
  
    // And find the maximum gradient amongst gradient bands
    var max_gradient = gradients.reduce(ee.Reducer.max());
  
    // Create a mask for band pixels that are the maximum gradient
    var gradmask = gradients.eq(max_gradient);
  
    // duplicate gradmask bands: each gradient represents 2 directions
    gradmask = gradmask.addBands(gradmask);
  
    // Determine the 8 directions
    var directions = sample_mean.select(1).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(7))).multiply(1);
    directions = directions.addBands(sample_mean.select(6).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(2))).multiply(2));
    directions = directions.addBands(sample_mean.select(3).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(5))).multiply(3));
    directions = directions.addBands(sample_mean.select(0).subtract(sample_mean.select(4)).gt(sample_mean.select(4).subtract(sample_mean.select(8))).multiply(4));
    // The next 4 are the not() of the previous 4
    directions = directions.addBands(directions.select(0).not().multiply(5));
    directions = directions.addBands(directions.select(1).not().multiply(6));
    directions = directions.addBands(directions.select(2).not().multiply(7));
    directions = directions.addBands(directions.select(3).not().multiply(8));
  
    // Mask all values that are not 1-8
    directions = directions.updateMask(gradmask);
  
    // "collapse" the stack into a singe band image (due to masking, each pixel has just one value (1-8) in it's directional band, and is otherwise masked)
    directions = directions.reduce(ee.Reducer.sum());  
  
    //var pal = ['ffffff','ff0000','ffff00', '00ff00', '00ffff', '0000ff', 'ff00ff', '000000'];
    //Map.addLayer(directions.reduce(ee.Reducer.sum()), {min:1, max:8, palette: pal}, 'Directions', false);
  
    var sample_stats = sample_var.divide(sample_mean.multiply(sample_mean));
  
    // Calculate localNoiseVariance
    var sigmaV = sample_stats.toArray().arraySort().arraySlice(0,0,5).arrayReduce(ee.Reducer.mean(), [0]);
  
    // Set up the 7*7 kernels for directional statistics
    var rect_weights = ee.List.repeat(ee.List.repeat(0,7),3).cat(ee.List.repeat(ee.List.repeat(1,7),4));
  
    var diag_weights = ee.List([[1,0,0,0,0,0,0], [1,1,0,0,0,0,0], [1,1,1,0,0,0,0], 
      [1,1,1,1,0,0,0], [1,1,1,1,1,0,0], [1,1,1,1,1,1,0], [1,1,1,1,1,1,1]]);
  
    var rect_kernel = ee.Kernel.fixed(7,7, rect_weights, 3, 3, false);
    var diag_kernel = ee.Kernel.fixed(7,7, diag_weights, 3, 3, false);

    // Create stacks for mean and variance using the original kernels. Mask with relevant direction.
    var dir_mean = img.reduceNeighborhood(ee.Reducer.mean(), rect_kernel).updateMask(directions.eq(1));
    var dir_var = img.reduceNeighborhood(ee.Reducer.variance(), rect_kernel).updateMask(directions.eq(1));
  
    dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), diag_kernel).updateMask(directions.eq(2)));
    dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), diag_kernel).updateMask(directions.eq(2)));
  
    // and add the bands for rotated kernels
    for (var i=1; i<4; i++) {
      dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), rect_kernel.rotate(i)).updateMask(directions.eq(2*i+1)));
      dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), rect_kernel.rotate(i)).updateMask(directions.eq(2*i+1)));
      dir_mean = dir_mean.addBands(img.reduceNeighborhood(ee.Reducer.mean(), diag_kernel.rotate(i)).updateMask(directions.eq(2*i+2)));
      dir_var = dir_var.addBands(img.reduceNeighborhood(ee.Reducer.variance(), diag_kernel.rotate(i)).updateMask(directions.eq(2*i+2)));
    }
  
    // "collapse" the stack into a single band image (due to masking, each pixel has just one value in it's directional band, and is otherwise masked)
    dir_mean = dir_mean.reduce(ee.Reducer.sum());
    dir_var = dir_var.reduce(ee.Reducer.sum());
  
    // A finally generate the filtered value
    var varX = dir_var.subtract(dir_mean.multiply(dir_mean).multiply(sigmaV)).divide(sigmaV.add(1.0));
  
    var b = varX.divide(dir_var);
    
    return dir_mean.add(b.multiply(img.subtract(dir_mean)))
      .arrayProject([0])
      // Get a multi-band image bands.
      .arrayFlatten([['sum']])
      .float();
  })).toBands().rename(bandNames);
  return powerToDb(ee.Image(result));
}