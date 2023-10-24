import {
  ConfigurationData,
  ConfigurationSchema,
  SchemaDefinition,
  SingleSchemaDefinition,
  MultipleSchemaDefinitions,
  ConfigurationAttributes,
} from '@models/adcm';
import { JSONValue, JSONObject, JSONPrimitive } from '@models/json';
import {
  ConfigurationObject,
  ConfigurationNode,
  ConfigurationNodeFilter,
  ConfigurationNodePath,
} from '../ConfigurationEditor.types';
import { validate as validateJsonSchema } from '@utils/jsonSchemaUtils';

export const validate = (schema: SchemaDefinition, configuration: JSONObject, attributes: ConfigurationAttributes) => {
  const { errorsPaths } = validateJsonSchema(schema, configuration);

  // ignore errors for not active groups
  for (const [path, value] of Object.entries(attributes)) {
    if (!value.isActive) {
      for (const [errorPath] of Object.entries(errorsPaths)) {
        if (errorPath.startsWith(path)) {
          delete errorsPaths[errorPath];
        }
      }
    }
  }

  const isValid = Object.keys(errorsPaths).length === 0;

  return { isValid, errorsPaths };
};

const getTitle = (keyName: string, fieldSchema: SingleSchemaDefinition) =>
  fieldSchema.title?.length ? fieldSchema.title : keyName;

const getDefaultFieldSchema = (parentFieldSchema: SingleSchemaDefinition | null): SingleSchemaDefinition => {
  const fieldSchema: SingleSchemaDefinition = {
    type: 'string',
    readOnly: false,
    adcmMeta: {
      activation: null,
      nullValue: null,
      isSecret: false,
      synchronization: null,
    },
  };

  if (parentFieldSchema?.adcmMeta.isSecret) {
    fieldSchema.adcmMeta.isSecret = true;
  }

  return fieldSchema;
};

export const buildTreeNodes = (
  schema: ConfigurationSchema,
  configuration: ConfigurationData,
  attributes: ConfigurationAttributes,
): ConfigurationNode => {
  const rootNode = buildRootNode(schema, configuration);
  fillFieldAttributes(rootNode, attributes);
  return rootNode;
};

const buildRootNode = (schema: ConfigurationSchema, configuration: ConfigurationData): ConfigurationNode => {
  const { fieldSchema } = determineFieldSchema(schema);
  const rootNode: ConfigurationNode = {
    key: 'root-node',
    data: {
      title: getTitle('Configuration', fieldSchema),
      type: 'object',
      path: [],
      parentNode: {} as ConfigurationNode,
      fieldSchema,
      isDeletable: false,
      isReadonly: true,
      objectType: 'structure',
      value: configuration,
    },
  };

  const children: ConfigurationNode[] = [];
  if (fieldSchema.properties) {
    for (const key of Object.keys(fieldSchema.properties)) {
      children.push(buildNode(key, [key], rootNode, fieldSchema.properties[key], configuration[key]));
    }
  }

  rootNode.children = children;

  return rootNode;
};

const fieldTypes = new Set(['string', 'integer', 'number', 'boolean']);

const buildNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SchemaDefinition,
  fieldValue: JSONValue,
): ConfigurationNode => {
  const { fieldSchema: singleFieldSchema, isNullable } = determineFieldSchema(fieldSchema);
  if (singleFieldSchema.type === 'object') {
    return buildObjectNode(fieldName, path, parentNode, singleFieldSchema, isNullable, fieldValue);
  } else if (singleFieldSchema.type === 'array') {
    return buildArrayNode(fieldName, path, parentNode, singleFieldSchema, isNullable, fieldValue);
  } else if (fieldTypes.has(singleFieldSchema.type as string)) {
    return buildFieldNode(fieldName, path, parentNode, singleFieldSchema, isNullable, fieldValue);
  } else if (singleFieldSchema.type === undefined && singleFieldSchema.enum) {
    return buildFieldNode(fieldName, path, parentNode, singleFieldSchema, isNullable, fieldValue);
  } else {
    return buildUnknownNode(fieldName, path, parentNode, singleFieldSchema);
  }
};

const buildObjectNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
  isNullable: boolean,
  fieldValue: JSONValue,
) => {
  const objectValue = fieldValue as JSONObject | null;
  const isArrayItem = parentNode.data.fieldSchema.type === 'array';
  const title = isArrayItem ? `${parentNode.data.title} [${fieldName}]` : getTitle(fieldName, fieldSchema);

  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      title,
      type: 'object',
      path,
      fieldSchema,
      parentNode,
      isDeletable: isArrayItem || isNullable,
      isReadonly: Boolean(fieldSchema.readOnly),
      objectType: 'map',
      value: fieldValue,
    },
  };

  const children = [];
  if (fieldSchema === undefined || fieldSchema.properties === undefined) {
    const fullPath = [...path, fieldName];
    console.error(`schema for /${fullPath.join('/')} not found`);
  } else {
    if (objectValue) {
      const addedFields = new Set();

      // add children from schema
      for (const key of Object.keys(fieldSchema.properties)) {
        const fieldPath = [...path, key];
        const propertyValue = objectValue?.[key] ?? null;
        const childrenFieldSchema = fieldSchema.properties[key];

        children.push(buildNode(key, fieldPath, node, childrenFieldSchema, propertyValue));
        addedFields.add(key);
      }

      // check if all props are required (object is structure)
      if (fieldSchema.required?.length && !fieldSchema.additionalProperties) {
        const areAllPropsRequired = fieldSchema.required.every((fieldName) => addedFields.has(fieldName));
        if (areAllPropsRequired) {
          (node.data as ConfigurationObject).objectType = 'structure';
        }
      }

      // add children from data (map case)
      for (const [key, propertyValue] of Object.entries(objectValue)) {
        if (!addedFields.has(key)) {
          const fieldPath = [...path, key];
          const childrenFieldSchema = fieldSchema.properties[key] ?? getDefaultFieldSchema(node.data.fieldSchema);

          children.push(buildNode(key, fieldPath, node, childrenFieldSchema, propertyValue));
          addedFields.add(key);
        }
      }

      if (fieldSchema.additionalProperties && !fieldSchema.readOnly) {
        children.push(buildAddFieldNode(path, node));
      }
    } else {
      children.push(buildAddEmptyObjectNode(path, fieldSchema, parentNode));
    }
  }

  if (children.length) {
    node.children = children;
  }

  return node;
};

const buildFieldNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
  isNullable: boolean,
  fieldValue: JSONValue,
) => {
  let isRequiredField = false;
  if (parentNode.data.fieldSchema.type === 'object') {
    const requiredFields = parentNode.data.fieldSchema.required ?? [];
    isRequiredField = requiredFields.includes(fieldName);
  }

  const isReadonly = Boolean(fieldSchema.readOnly);

  const isArrayItem = parentNode.data.fieldSchema.type === 'array';
  const title = isArrayItem ? `${parentNode.data.title} [${fieldName}]` : getTitle(fieldName, fieldSchema);

  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      title,
      type: 'field',
      path,
      parentNode,
      fieldSchema,
      value: fieldValue as JSONPrimitive,
      isDeletable: !isReadonly && (!isRequiredField || isNullable),
      isReadonly: isReadonly,
    },
  };

  return node;
};

const buildAddEmptyObjectNode = (
  path: ConfigurationNodePath,
  fieldSchema: SingleSchemaDefinition,
  parentNode: ConfigurationNode,
) => {
  // const fieldSchema: SingleSchemaDefinition = getDefaultFieldSchema(parentNode.data.fieldSchema);

  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      type: 'addEmptyObject',
      title: 'Add',
      path,
      parentNode,
      fieldSchema,
    },
  };

  return node;
};

const buildAddFieldNode = (path: ConfigurationNodePath, parentNode: ConfigurationNode) => {
  const fieldSchema: SingleSchemaDefinition = getDefaultFieldSchema(parentNode.data.fieldSchema);

  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      type: 'addField',
      title: 'Add property',
      path,
      parentNode,
      fieldSchema,
    },
  };

  return node;
};

const buildArrayNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
  isNullable: boolean,
  fieldValue: JSONValue,
) => {
  const array = fieldValue as Array<JSONValue> | null;
  const itemsSchema = fieldSchema.items as SingleSchemaDefinition;

  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      title: getTitle(fieldName, fieldSchema),
      type: 'array',
      path,
      parentNode,
      fieldSchema,
      isReadonly: Boolean(fieldSchema.readOnly),
      isDeletable: isNullable,
      value: array,
    },
  };

  node.children = [];

  if (array) {
    for (let i = 0; i < array.length; i++) {
      const elementPath = [...path, i];
      node.children.push(buildArrayItemNode(i.toString(), elementPath, node, itemsSchema, array[i]));
    }
  }

  if (!node.data.fieldSchema.readOnly) {
    node.children.push(buildAddArrayItemNode(path, node, itemsSchema));
  }

  return node;
};

const buildArrayItemNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
  fieldValue: JSONValue,
) => {
  return buildNode(fieldName, path, parentNode, fieldSchema, fieldValue);
};

const buildAddArrayItemNode = (
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
) => {
  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      type: 'addArrayItem',
      title: '1',
      path,
      parentNode,
      fieldSchema,
    },
  };

  return node;
};

const buildUnknownNode = (
  fieldName: string,
  path: ConfigurationNodePath,
  parentNode: ConfigurationNode,
  fieldSchema: SingleSchemaDefinition,
) => {
  const node: ConfigurationNode = {
    key: buildKey(path),
    data: {
      title: `UNKNOWN FIELD: ${fieldName}, TYPE: ${fieldSchema.type}`,
      type: 'field',
      path,
      parentNode,
      fieldSchema,
      value: 'some value',
      isDeletable: false,
      isReadonly: true,
    },
  };

  return node;
};

const buildKey = (path: ConfigurationNodePath) => `/${path.join('/')}`;

export const filterTreeNodes = (tree: ConfigurationNode, filter: ConfigurationNodeFilter) => {
  tree.children = tree.children?.filter((node) => filterRecursively(node, filter));
  return tree;
};

const filterRecursively = (tree: ConfigurationNode, filter: ConfigurationNodeFilter) => {
  if (tree.data.type === 'addArrayItem' || tree.data.type === 'addField') {
    return true;
  }

  const foundInTitle = tree.data.title.toLowerCase().includes(filter.title.toLowerCase());
  const isVisible =
    (filter.showInvisible ? true : !tree.data.fieldSchema.adcmMeta.isInvisible) &&
    (filter.showAdvanced ? true : !tree.data.fieldSchema.adcmMeta.isAdvanced);

  tree.children = tree.children?.filter((node) => filterRecursively(node, filter));

  if (!foundInTitle && tree.children?.length === 1) {
    const singleChildType = tree.children[0].data.type;
    if (singleChildType === 'addArrayItem' || singleChildType === 'addField') {
      tree.children = undefined;
    }
  }

  const foundInChildren = Boolean(tree.children?.length);
  if ((foundInTitle || foundInChildren) && isVisible) {
    return true;
  }

  return false;
};

const fillFieldAttributes = (tree: ConfigurationNode, attributes: ConfigurationAttributes) => {
  tree.data.fieldAttributes = attributes[tree.key];
  if (tree.children) {
    for (const child of tree.children) {
      fillFieldAttributes(child, attributes);
    }
  }
};

const isSingleSchemaDefinition = (fieldSchema: SchemaDefinition): fieldSchema is SingleSchemaDefinition => {
  return (fieldSchema as MultipleSchemaDefinitions).oneOf === undefined;
};

const determineFieldSchema = (
  fieldSchema: SchemaDefinition,
): { isNullable: boolean; fieldSchema: SingleSchemaDefinition } => {
  if (isSingleSchemaDefinition(fieldSchema)) {
    return {
      isNullable: false,
      fieldSchema,
    };
  } else {
    const [schema1, schema2] = fieldSchema.oneOf ?? [];

    if (schema1.type === null) {
      return { isNullable: true, fieldSchema: schema2 as SingleSchemaDefinition };
    } else {
      return { isNullable: true, fieldSchema: schema1 as SingleSchemaDefinition };
    }
  }
};