# Integración SAPUI5 ↔ OData (V2 y V4)

Guía para consumir servicios OData ABAP (SEGW/RAP) desde aplicaciones SAPUI5/Fiori.

---

## Decidir entre OData V2 y OData V4

| Criterio | OData V2 (SEGW) | OData V4 (RAP) |
|---|---|---|
| Sistema target | SAP ERP / S/4HANA ≤ 2020 | S/4HANA 2021+ |
| Draft handling | Manual (DraftEnabled) | Nativo en RAP |
| Fiori Elements | List Report, Object Page V2 | List Report, Object Page V4, Worklist |
| SAPUI5 model | `sap.ui.model.odata.v2.ODataModel` | `sap.ui.model.odata.v4.ODataModel` |
| Filtros $filter | Limitado | Completo (operadores lambda) |

---

## Estructura de una app SAPUI5 con OData

```
webapp/
├── manifest.json          ← Registro de dataSources y modelos
├── Component.js           ← Inicialización de modelos
├── controller/
│   └── Main.controller.js ← Lógica de vinculación y operaciones
├── view/
│   └── Main.view.xml      ← UI con bindings OData
└── model/
    └── formatter.js       ← Formateo de valores
```

---

## manifest.json — Registro del servicio OData

### Para OData V2 (SEGW)

```json
{
  "sap.app": {
    "dataSources": {
      "mainService": {
        "uri": "/sap/opu/odata/sap/Z<NOMBRE>_SRV/",
        "type": "OData",
        "settings": {
          "odataVersion": "2.0"
        }
      }
    }
  },
  "sap.ui5": {
    "models": {
      "": {
        "dataSource": "mainService",
        "preload": true,
        "settings": {
          "useBatch": true,
          "refreshAfterChange": true
        }
      }
    }
  }
}
```

### Para OData V4 (RAP)

```json
{
  "sap.app": {
    "dataSources": {
      "mainService": {
        "uri": "/sap/opu/odata4/sap/<SERVICE_BINDING>/srvd/sap/<SERVICE_DEF>/0001/",
        "type": "OData",
        "settings": {
          "odataVersion": "4.0"
        }
      }
    }
  },
  "sap.ui5": {
    "models": {
      "": {
        "dataSource": "mainService",
        "preload": true,
        "settings": {
          "operationMode": "Server",
          "synchronizationMode": "None",
          "autoExpandSelect": true
        }
      }
    }
  }
}
```

---

## Operaciones CRUD en el controlador

### OData V2: Leer lista

```javascript
// En el controlador
onInit: function () {
  var oModel = this.getView().getModel(); // ODataModel V2 del manifest

  // Opción 1: binding directo en la vista (recomendado para tablas)
  var oTable = this.byId("salesOrderTable");
  oTable.bindItems({
    path: "/SalesOrderSet",
    filters: [
      new Filter("Status", FilterOperator.EQ, "A")
    ],
    parameters: {
      "$expand": "ToItems",
      "$top": 50
    }
  });
},
```

### OData V2: Leer entidad individual

```javascript
onSelectOrder: function (sOrderId) {
  var oModel = this.getView().getModel();

  oModel.read("/SalesOrderSet('" + sOrderId + "')", {
    urlParameters: { "$expand": "ToItems" },
    success: function (oData) {
      // oData contiene el pedido con sus ítems
      this._processOrder(oData);
    }.bind(this),
    error: function (oError) {
      MessageBox.error("Error al leer pedido: " + oError.message);
    }
  });
},
```

### OData V2: Crear entidad

```javascript
onCreate: function () {
  var oModel  = this.getView().getModel();
  var oNewEntry = {
    CustomerId:  this.byId("custInput").getValue(),
    NetAmount:   this.byId("amountInput").getValue(),
    Currency:    "EUR"
  };

  oModel.create("/SalesOrderSet", oNewEntry, {
    success: function (oData) {
      MessageToast.show("Pedido " + oData.SalesOrderId + " creado.");
      oModel.refresh();
    },
    error: function (oError) {
      var sMsg = JSON.parse(oError.responseText).error.message.value;
      MessageBox.error(sMsg);
    }
  });
},
```

### OData V2: Actualizar entidad

```javascript
onUpdate: function (sOrderId) {
  var oModel = this.getView().getModel();
  var oContext = oModel.getContext("/SalesOrderSet('" + sOrderId + "')");

  // Editar via Context binding
  oModel.setProperty("/SalesOrderSet('" + sOrderId + "')/Status", "C");
  oModel.submitChanges({
    success: function () { MessageToast.show("Actualizado."); },
    error: function (oError) { MessageBox.error("Error al actualizar."); }
  });
},
```

### OData V2: Eliminar entidad

```javascript
onDelete: function (sOrderId) {
  var oModel = this.getView().getModel();
  oModel.remove("/SalesOrderSet('" + sOrderId + "')", {
    success: function () { MessageToast.show("Eliminado."); },
    error: function () { MessageBox.error("Error al eliminar."); }
  });
},
```

### OData V2: Llamar Function Import

```javascript
onApprove: function (sOrderId) {
  var oModel = this.getView().getModel();

  oModel.callFunction("/ApproveOrder", {
    method: "POST",
    urlParameters: { OrderId: sOrderId },
    success: function (oData) {
      MessageToast.show("Pedido aprobado.");
    },
    error: function (oError) {
      MessageBox.error("No se pudo aprobar.");
    }
  });
},
```

---

## OData V4: Operaciones en controlador

### Leer lista (binding)

```javascript
// En la vista XML (Fiori Elements genera esto automáticamente)
// <Table items="{path: '/SalesOrder', parameters: {$expand: 'to_Items'}}">

// En controlador manual:
onInit: function () {
  var oList = this.byId("salesOrderList");
  var oBinding = oList.getBinding("items");
  oBinding.filter([
    new Filter("Status", FilterOperator.EQ, "A")
  ]);
},
```

### Acción RAP (OData V4 Action)

```javascript
onApprove: function (oContext) {
  // oContext es el contexto del objeto seleccionado
  var oAction = oContext.getModel().bindContext(
    "com.sap.gateway.default.zui_salesorder_o4_0001.v0001.approve(...)",
    oContext
  );

  oAction.invoke().then(function () {
    MessageToast.show("Aprobado.");
    oContext.refresh();
  }).catch(function (oError) {
    MessageBox.error(oError.message);
  });
},
```

---

## Vista XML — Bindings de ejemplo

### Lista de entidades

```xml
<Table id="salesOrderTable"
       items="{
         path: '/SalesOrderSet',
         parameters: { expand: 'ToCustomer' },
         sorter: { path: 'CreationDate', descending: true }
       }">
  <columns>
    <Column><Text text="Pedido"/></Column>
    <Column><Text text="Cliente"/></Column>
    <Column><Text text="Importe"/></Column>
  </columns>
  <items>
    <ColumnListItem>
      <cells>
        <Text text="{SalesOrderId}"/>
        <Text text="{ToCustomer/CustomerName}"/>
        <ObjectNumber
          number="{
            path: 'NetAmount',
            type: 'sap.ui.model.type.Currency',
            parts: ['NetAmount', 'Currency']
          }"
          unit="{Currency}"/>
      </cells>
    </ColumnListItem>
  </items>
</Table>
```

### Detalle con Object Page manual

```xml
<VBox>
  <form:SimpleForm editable="true" layout="ResponsiveGridLayout">
    <form:content>
      <Label text="ID Pedido"/>
      <Input value="{SalesOrderId}" enabled="false"/>
      <Label text="Cliente"/>
      <Input value="{CustomerId}"/>
      <Label text="Importe"/>
      <Input value="{
        path: 'NetAmount',
        type: 'sap.ui.model.type.Float',
        formatOptions: { decimals: 2 }
      }"/>
    </form:content>
  </form:SimpleForm>
</VBox>
```

---

## Proxy / cors-bypass en desarrollo local

Para llamadas desde localhost a un sistema SAP remoto, configurar el proxy en `ui5.yaml`:

```yaml
server:
  customMiddleware:
    - name: ui5-middleware-simpleproxy
      mountPath: /sap
      configuration:
        baseUri: "https://<SAP_HOST>:<PORT>"
        strictSSL: false
```

---

## Fiori Elements: Anotaciones ABAP necesarias

Para Fiori Elements List Report + Object Page, las CDS Projection Views deben tener:

```abap
" Cabecera del objeto
@UI.headerInfo: {
  typeName:       'Pedido',
  typeNamePlural: 'Pedidos',
  title:          { type: #STANDARD, value: 'SalesOrderId' },
  description:    { type: #STANDARD, value: 'CustomerName' }
}

" Campos en la lista
@UI.lineItem: [{ position: 10 }]
SalesOrderId,

@UI.lineItem: [{ position: 20 }]
CustomerName,

" Campo de búsqueda
@UI.selectionField: [{ position: 10 }]
SalesOrderId,

@UI.selectionField: [{ position: 20 }]
Status,

" Facetas del Object Page
@UI.facet: [{
  id:       'GeneralFacet',
  purpose:  #STANDARD,
  type:     #IDENTIFICATION_REFERENCE,
  label:    'Información General',
  position: 10
}]

" Campos del formulario de detalle
@UI.identification: [{ position: 10 }]
SalesOrderId,
```

---

## Checklist integración ABAP ↔ SAPUI5

- [ ] Servicio OData registrado y activo en `/IWFND/MAINT_SERVICE` (V2) o publicado en Service Binding (V4).
- [ ] URL del servicio verificada en navegador / Postman antes de integrar en la app.
- [ ] `manifest.json` apunta a la URI correcta con versión OData correcta.
- [ ] Nombres de Entity Set/Property coinciden exactamente con los definidos en SEGW / CDS Projection.
- [ ] Manejo de errores OData implementado en el controlador (success/error callbacks).
- [ ] Autorización ABAP configurada (roles SAP) para el usuario de prueba.
- [ ] CSRF token gestionado (automático en ODataModel V2 con `useBatch: true`).
- [ ] Expandir navegaciones necesarias (`$expand`) para evitar llamadas adicionales.
