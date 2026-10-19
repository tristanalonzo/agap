// Prints the vector layer names inside each NOAH flood PMTiles file.
// Run from frontend/: node scripts/print-pmtiles-layers.mjs
import { PMTiles } from "pmtiles";

const BASE =
  "https://huggingface.co/datasets/bettergovph/project-noah-hazard-maps/resolve/main/PMTiles/layers/";
const FILES = ["flood_5yr.pmtiles", "flood_25yr.pmtiles", "flood_100yr.pmtiles"];

for (const file of FILES) {
  try {
    const archive = new PMTiles(BASE + file);
    const header = await archive.getHeader();
    const metadata = await archive.getMetadata();
    const layers = (metadata.vector_layers ?? []).map((layer) => layer.id);
    console.log(`${file}: layers = ${JSON.stringify(layers)}, zoom ${header.minZoom}-${header.maxZoom}`);
    for (const layer of metadata.vector_layers ?? []) {
      console.log(`  ${layer.id} fields: ${JSON.stringify(layer.fields ?? {})}`);
    }
  } catch (error) {
    console.log(`${file}: FAILED - ${error.message}`);
  }
}
