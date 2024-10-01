import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('/mnt/nvme1n1/CurePilot/XML_Parser/AdministeredDrugEx.hbm.xml')
root = tree.getroot()

# Define the namespace
namespace = {'ns': 'urn:nhibernate-mapping-2.2'}

# Extract and print class details
def print_class_details(class_element):
    class_name = class_element.attrib['name']
    class_table = class_element.attrib['table']
    print(f"Class Name: {class_name}")
    print(f"Class Table: {class_table}\n")

    # Extract and print ID details
    id_element = class_element.find('ns:id', namespace)
    id_name = id_element.attrib['name']
    id_column = id_element.attrib['column']
    print(f"ID Name: {id_name}")
    print(f"ID Column: {id_column}\n")

    # Extract and print property details
    print("Properties:")
    for prop in class_element.findall('ns:property', namespace):
        prop_name = prop.attrib['name']
        prop_column = prop.attrib['column']
        prop_type = prop.attrib['type']
        print(f"  - Name: {prop_name}, Column: {prop_column}, Type: {prop_type}")
    
    # Extract and print bag details
    print("\nBags:")
    for bag in class_element.findall('ns:bag', namespace):
        bag_name = bag.attrib['name']
        print(f"  - Bag Name: {bag_name}")
        key = bag.find('ns:key', namespace)
        key_column = key.attrib['column']
        print(f"    Key Column: {key_column}")
        one_to_many = bag.find('ns:one-to-many', namespace)
        one_to_many_class = one_to_many.attrib['class']
        print(f"    One to Many Class: {one_to_many_class}")

# Find the class element
class_element = root.find('ns:class', namespace)

# Print the class details
print_class_details(class_element)


# # import xml.etree.ElementTree as ET
# # from anytree import Node, RenderTree
# # from anytree.exporter import DotExporter

# # # Parse the XML file
# # tree = ET.parse('/mnt/nvme1n1/CurePilot/XML_Parser/AdministeredDrugEx.hbm.xml')
# # root = tree.getroot()

# # # Define the namespace
# # namespace = {'ns': 'urn:nhibernate-mapping-2.2'}

# # # Function to build the tree
# # def build_tree(element, parent_node=None):
# #     name = element.attrib.get('name')
# #     table = element.attrib.get('table')
# #     node_name = f"{name} ({table})" if table else name
# #     node = Node(node_name, parent=parent_node)

# #     for subclass in element.findall('ns:subclass', namespace):
# #         build_tree(subclass, node)

# #     return node

# # # Find the root class element
# # class_element = root.find('ns:class', namespace)

# # # Build the inheritance tree
# # root_node = build_tree(class_element)

# # # Print the tree structure
# # for pre, fill, node in RenderTree(root_node):
# #     print("%s%s" % (pre, node.name))

# # # Export the tree to a .dot file (Graphviz format)
# # DotExporter(root_node).to_dotfile("inheritance_tree.dot")

# # # Optionally, save the tree structure in a readable text format
# # with open("inheritance_tree.txt", "w") as f:
# #     for pre, fill, node in RenderTree(root_node):
# #         f.write("%s%s\n" % (pre, node.name))

# import xml.etree.ElementTree as ET
# import json
# import csv
# import pandas as pd
# import xmltodict

# # Parse the XML file
# tree = ET.parse('/mnt/nvme1n1/CurePilot/XML_Parser/AdministeredDrugEx.hbm.xml')
# root = tree.getroot()

# # Define the namespace
# namespace = {'ns': 'urn:nhibernate-mapping-2.2'}

# # Function to extract data from XML and organize it in a dictionary
# def extract_data(element):
#     data = {
#         'name': element.attrib.get('name'),
#         'table': element.attrib.get('table'),
#         'id': None,
#         'version': None,
#         'properties': [],
#         'bags': []
#     }

#     # Extract id details
#     id_element = element.find('ns:id', namespace)
#     if id_element is not None:
#         data['id'] = {
#             'name': id_element.attrib.get('name'),
#             'column': id_element.attrib.get('column'),
#             'type': id_element.attrib.get('type')
#         }

#     # Extract version details
#     version_element = element.find('ns:version', namespace)
#     if version_element is not None:
#         data['version'] = {
#             'name': version_element.attrib.get('name'),
#             'column': version_element.attrib.get('column'),
#             'type': version_element.attrib.get('type')
#         }

#     # Extract property details
#     for prop in element.findall('ns:property', namespace):
#         data['properties'].append({
#             'name': prop.attrib.get('name'),
#             'column': prop.attrib.get('column'),
#             'type': prop.attrib.get('type'),
#             'length': prop.attrib.get('length'),
#             'not-null': prop.attrib.get('not-null')
#         })

#     # Extract bag details
#     for bag in element.findall('ns:bag', namespace):
#         bag_data = {
#             'name': bag.attrib.get('name'),
#             'inverse': bag.attrib.get('inverse'),
#             'lazy': bag.attrib.get('lazy'),
#             'cascade': bag.attrib.get('cascade'),
#             'order-by': bag.attrib.get('order-by'),
#             'where': bag.attrib.get('where'),
#             'key_column': bag.find('ns:key', namespace).attrib.get('column'),
#             'one_to_many_class': bag.find('ns:one-to-many', namespace).attrib.get('class')
#         }
#         data['bags'].append(bag_data)

#     return data

# # Extract data from the root class element
# class_element = root.find('ns:class', namespace)
# data = extract_data(class_element)

# # Save as JSON
# with open('data.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

# # Save as CSV
# # Properties
# properties_df = pd.DataFrame(data['properties'])
# properties_df.to_csv('properties.csv', index=False)

# # Bags
# bags_df = pd.DataFrame(data['bags'])
# bags_df.to_csv('bags.csv', index=False)

# # Save as Text
# with open('data.txt', 'w', encoding='utf-8') as f:
#     f.write(json.dumps(data, indent=4))

# # Save as XML (using xmltodict for pretty format)
# with open('data.xml', 'w', encoding='utf-8') as f:
#     f.write(xmltodict.unparse({'root': data}, pretty=True))