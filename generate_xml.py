import os
import zipfile
import xml.etree.ElementTree as ET

PLUGIN_BASE_DIR = "./output"
REPO_URL = "https://your-username.github.io/intellij-plugin-repo"
OUTPUT_XML = os.path.join(PLUGIN_BASE_DIR, "updatePlugins.xml")

def extract_plugin_metadata(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        plugin_xml_path = next((n for n in z.namelist() if n.endswith("plugin.xml") and "META-INF" in n), None)
        if not plugin_xml_path:
            return None
        with z.open(plugin_xml_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            return {
                "id": root.findtext('id') or root.findtext('name'),
                "name": root.findtext('name'),
                "version": root.findtext('version'),
                "vendor": root.findtext('vendor'),
                "description": root.findtext('description') or ""
            }

def generate_update_xml():
    plugins = ET.Element("plugins")
    for plugin_dir in os.listdir(PLUGIN_BASE_DIR):
        path = os.path.join(PLUGIN_BASE_DIR, plugin_dir)
        if not os.path.isdir(path):
            continue
        zips = [f for f in os.listdir(path) if f.endswith(".zip")]
        if not zips:
            continue
        latest = sorted(zips)[-1]
        zip_path = os.path.join(path, latest)
        meta = extract_plugin_metadata(zip_path)
        if not meta:
            continue

        plugin = ET.SubElement(plugins, "plugin")
        ET.SubElement(plugin, "id").text = meta["id"]
        ET.SubElement(plugin, "name").text = meta["name"]
        ET.SubElement(plugin, "version").text = meta["version"]
        ET.SubElement(plugin, "vendor").text = meta["vendor"]
        desc = ET.SubElement(plugin, "description")
        doc_url = f"{REPO_URL}/{plugin_dir}/index.html"
        if os.path.exists(os.path.join(path, "index.html")):
            meta["description"] += f"\n\n<a href='{doc_url}'>Full documentation</a>"
        desc.text = f"<![CDATA[{meta['description']}]]>"
        ET.SubElement(plugin, "download-url").text = f"{REPO_URL}/{plugin_dir}/{latest}"
    tree = ET.ElementTree(plugins)
    tree.write(OUTPUT_XML, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    generate_update_xml()
