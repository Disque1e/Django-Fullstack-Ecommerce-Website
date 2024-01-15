from django.contrib.auth import authenticate
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import connection
from . import forms
from . import models
from .database import mongoCon
from django.http import HttpResponse, JsonResponse
import json

# Create your views here.

@login_required(login_url="Login")
def home(request):
    return redirect(list_equipments)

# Auth views

def signup(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(login_view)

    context={'form': form}
    return render(request, 'app/authentication/signup.html', context=context)

def login_view(request):
    form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect(home)
    context = {'form': form}
    return render(request, 'app/authentication/login.html', context=context)

def logout_view(request):
    auth.logout(request)
    return redirect(login_view)

# CRUD Actions - Suppliers Table

def list_warehouses(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_warehouses()')
        columns = [col[0] for col in cursor.description]
        warehouses = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {'warehouses': warehouses}
    return render(request, 'app/suppliers/warehouses/warehouses-list.html', context=context)

def create_warehouse(request):
    if request.method == 'POST':
        form = forms.WarehousesForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'CALL insert_warehouse(%s, %s, %s, %s)',
                        [
                            form_data['address'],
                            form_data['city'],
                            form_data['postal_code'],
                            form_data['country'],
                        ]
                    )
            except Exception as e:
                print(request, f"Error creating warehouse: {e}")
                return redirect(list_warehouses)
            return redirect(list_warehouses)
    else:
        form = forms.WarehousesForm()
    
    context = {'form': form}
    return render(request, 'app/suppliers/warehouses/add-warehouse.html', context=context)

def edit_warehouse(request, id):
    warehouse = get_object_or_404(models.warehouse, warehouse_id=id)
    if request.method == 'POST':
        form = forms.WarehousesForm(request.POST, instance=warehouse)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_warehouse(%s, %s, %s, %s, %s)',
                    [
                        id,
                        form_data['address'],
                        form_data['city'],
                        form_data['postal_code'],
                        form_data['country'],
                    ]
                )
            return redirect(list_warehouses)
    else:
        form = forms.WarehousesForm(instance=warehouse)

    context = {'form': form, 'warehouse': warehouse}
    return render(request, 'app/suppliers/warehouses/edit-warehouse.html', context=context)

def delete_warehouse(request, id):
    warehouse = get_object_or_404(models.warehouse, warehouse_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_warehouse(%s)', [id])
    return redirect(list_warehouses)

# CRUD Actions - Suppliers Table

def list_suppliers(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_suppliers()')
        columns = [col[0] for col in cursor.description]
        suppliers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        aggregated_suppliers = {}
        for supplier in suppliers:
            id = supplier['supplier_id']

            if id in aggregated_suppliers:
                aggregated_suppliers[id]['addresses'].append(supplier['address'])
                aggregated_suppliers[id]['cities'].append(supplier['city'])
                aggregated_suppliers[id]['postal_codes'].append(supplier['postal_code'])
                aggregated_suppliers[id]['countries'].append(supplier['country'])

            else:
                supplier['addresses'] = [supplier['address']]
                supplier['cities'] = [supplier['city']]
                supplier['postal_codes'] = [supplier['postal_code']]
                supplier['countries'] = [supplier['country']]
                aggregated_suppliers[id] = supplier

    for supplier in aggregated_suppliers.values():
        supplier['address_info'] = zip(
            supplier['addresses'],
            supplier['cities'],
            supplier['postal_codes'],
            supplier['countries']
        )

    context = {'suppliers': list(aggregated_suppliers.values())}
    return render(request, 'app/suppliers/suppliers-list.html', context=context)

def create_supplier(request):
    if request.method == 'POST':
        form = forms.SupplierForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    warehouse_ids = form_data['warehouse'].values_list('warehouse_id', flat=True)
                    cursor.execute(
                        'CALL insert_supplier(%s, %s, %s, %s)',
                        [
                            form_data['name'],
                            form_data['phone_number'],
                            form_data['email'],
                            list(warehouse_ids),  # Convert to a list for the procedure
                        ]
                    )
            except Exception as e:
                print(request, f"Error creating supplier: {e}")
                return redirect(list_suppliers)
            return redirect(list_suppliers)
    else:
        form = forms.SupplierForm()
    
    context = {'form': form}
    return render(request, 'app/suppliers/add-supplier.html', context=context)

def edit_supplier(request, id):
    supplier = get_object_or_404(models.supplier, supplier_id=id)
    if request.method == 'POST':
        form = forms.SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                warehouse_ids = form_data['warehouse'].values_list('warehouse_id', flat=True)
                cursor.execute(
                    'CALL edit_supplier(%s, %s, %s, %s, %s)',
                    [
                        id,
                        form_data['name'],
                        form_data['phone_number'],
                        form_data['email'],
                        list(warehouse_ids),
                    ]
                )
            return redirect(list_suppliers)
    else:
        form = forms.SupplierForm(instance=supplier)

    context = {'form': form, 'supplier': supplier}
    return render(request, 'app/suppliers/edit-supplier.html', context=context)

def delete_supplier(request, id):
    supplier = get_object_or_404(models.supplier, supplier_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_supplier(%s)', [id])
    return redirect(list_suppliers)

# CRUD Actions - Component Type Table

def list_component_types(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_component_types()')
        columns = [col[0] for col in cursor.description]
        component_types = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {'component_types': component_types}
    return render(request, 'app/components/component-type/component-types-list.html', context=context)

def create_component_type(request):
    if request.method == 'POST':
        form = forms.ComponentTypeForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'CALL insert_component_type(%s, %s)',
                        [
                            form_data['type_name'],
                            form_data['description'],
                        ]
                    )
            except:
                # Handle integrity violation (e.g., duplicate key, unique constraint)
                # Log or handle the error appropriately
                pass
            return redirect(list_component_types)
    else:
        form = forms.ComponentTypeForm()
    
    context = {'form': form}
    return render(request, 'app/components/component-type/add-component-type.html', context=context)


def edit_component_type(request, id):
    component = get_object_or_404(models.component_type, component_type_id=id)
    if request.method == 'POST':
        form = forms.ComponentTypeForm(request.POST, instance=component)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_component_type(%s, %s, %s)',
                    [
                        id,
                        form_data['type_name'],
                        form_data['description'],
                    ]
                )
            return redirect(list_component_types)
    else:
        form = forms.ComponentTypeForm(instance=component)

    context = {'form': form, 'component': component}
    return render(request, 'app/components/component-type/edit-component-type.html', context=context)

def delete_component_type(request, id):
    component_type = get_object_or_404(models.component_type, component_type_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_component_type(%s)', [id])
    return redirect(list_component_types)

# CRUD Actions - Components Table

def list_components(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_components()')
        columns = [col[0] for col in cursor.description]
        components = [dict(zip(columns, row)) for row in cursor.fetchall()]

        components = [component for component in components if component['stock'] > 0]

        aggregated_components = {}
        for component in components:
            name = component['name']
            type = component['component_type_id']
            key = (name, type)

            if key in aggregated_components:
                aggregated_components[key]['serial_numbers'].append(component['serial_number'])
                aggregated_components[key]['purchase_dates'].append(component['purchase_date'])
                aggregated_components[key]['purchase_prices'].append(component['purchase_price'])
                aggregated_components[key]['suppliers'].append(component['supplier_name'])
                aggregated_components[key]['edit_url'] = reverse('EditComponent', args=[component['component_id']])
                aggregated_components[key]['delete_url'] = reverse('DeleteComponent', args=[component['component_id']])
                aggregated_components[key]['stock'] += component['stock']
            else:
                component['serial_numbers'] = [component['serial_number']]
                component['purchase_dates'] = [component['purchase_date']]
                component['purchase_prices'] = [component['purchase_price']]
                component['suppliers'] = [component['supplier_name']]
                aggregated_components[key] = component

    context = {'components': list(aggregated_components.values())}
    return render(request, 'app/components/components-list.html', context=context)

def components_detail(request, name, component_type_id):
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT 
                c.component_id,
                c.component_type_id,
                c.supplier_id,
                c.name,
                c.serial_number,
                c.purchase_date,
                c.purchase_price,
                c.image,
                s.name as supplier_name,
                ct.type_name
            FROM app_components c JOIN app_supplier s 
                ON c.supplier_id = s.supplier_id JOIN app_component_type ct 
                    ON ct.component_type_id = c.component_type_id 
            WHERE (c.name = %s AND c.component_type_id = %s) AND c.stock > 0''', [name, component_type_id]
        )
        columns = [col[0] for col in cursor.description]
        components = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {'components': components}
    return render(request, 'app/components/components-details.html', context=context)
    
def create_component(request):
    if request.method == 'POST':
        form = forms.ComponentForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'CALL insert_component(%s, %s, %s, %s, %s, %s, %s)',
                        [
                            form_data['component_type'].component_type_id,
                            form_data['supplier'].supplier_id,
                            form_data['name'],
                            form_data['serial_number'],
                            form_data['purchase_date'],
                            form_data['purchase_price'],
                            form_data['image'],
                        ]
                    )
            except Exception as e:
                print(request, f"Error creating component: {e}")
                return redirect(list_components)
            return redirect(list_components)
    else:
        form = forms.ComponentForm()
    
    context = {'form': form}
    print(context)
    return render(request, 'app/components/add-components.html', context=context)


def edit_component(request, id):
    component = get_object_or_404(models.components, component_id=id)
    if request.method == 'POST':
        form = forms.ComponentForm(request.POST, instance=component)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_component(%s, %s, %s, %s, %s, %s, %s, %s)',
                    [
                        id,
                        form_data['component_type'].component_type_id,
                        form_data['supplier'].supplier_id,
                        form_data['name'],
                        form_data['serial_number'],
                        form_data['purchase_date'],
                        form_data['purchase_price'],
                        form_data['image'],
                    ]
                )
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM app_components WHERE name = %s', [component.name])
                count = cursor.fetchone()[0]

            if count > 1:
                return redirect(components_detail, name=component.name, component_type_id=component.component_type.component_type_id)
            else:
                return redirect(list_components)    
    else:
        form = forms.ComponentForm(instance=component)

    context = {'form': form, 'component': component}
    return render(request, 'app/components/edit-component.html', context=context)

def delete_component(request, id):
    component = get_object_or_404(models.components, component_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_component(%s)', [id])

    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM app_components WHERE name = %s', [component.name])
        count = cursor.fetchone()[0]

    if count > 1:
        return redirect(components_detail, name=component.name)
    else:
        return redirect(list_components)

# CRUD Actions - Equipment Type Table

def list_equipment_types(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_equipment_types()')
        columns = [col[0] for col in cursor.description]
        equipment_types = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {'equipment_types': equipment_types}
    return render(request, 'app/equipments/equipment-type/equipment-types-list.html', context=context)

def create_equipment_type(request):
    if request.method == 'POST':
        form = forms.EquipmentTypeForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'CALL insert_equipment_type(%s, %s)',
                        [
                            form_data['type_name'],
                            form_data['description'],
                        ]
                    )
            except:
                # Handle integrity violation (e.g., duplicate key, unique constraint)
                # Log or handle the error appropriately
                pass
            return redirect(list_equipment_types)
    else:
        form = forms.EquipmentTypeForm()
    
    context = {'form': form}
    return render(request, 'app/equipments/equipment-type/add-equipment-type.html', context=context)

def edit_equipment_type(request, id):
    equipment_types = get_object_or_404(models.equipment_type, equipment_type_id=id)
    if request.method == 'POST':
        form = forms.EquipmentTypeForm(request.POST, instance=equipment_types)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_equipment_type(%s, %s, %s)',
                    [
                        id,
                        form_data['type_name'],
                        form_data['description'],
                    ]
                )
            return redirect(list_equipment_types)
    else:
        form = forms.EquipmentTypeForm(instance=equipment_types)

    context = {'form': form, 'equipment_types': equipment_types}
    return render(request, 'app/equipments/equipment-type/edit-equipment-type.html', context=context)

def delete_equipment_type(request, id):
    equipment_types = get_object_or_404(models.equipment_type, equipment_type_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_equipment_type(%s)', [id])
    return redirect(list_equipment_types)

# CRUD Actions - Equipments Table

def list_equipments(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_equipments()')
        columns = [col[0] for col in cursor.description]
        equipments = [dict(zip(columns, row)) for row in cursor.fetchall()]

        aggregated_equipments= {}
        for equipment in equipments:
            serial_number = equipment['serial_number']

            if serial_number in aggregated_equipments:
                aggregated_equipments[serial_number]['components'].append(equipment['component_name'])
            else:
                equipment['components'] = [equipment['component_name']]
                aggregated_equipments[serial_number] = equipment

    context = {'equipments': list(aggregated_equipments.values())}
    return render(request, 'app/equipments/equipments-list.html', context=context)

def create_equipment(request):
    if request.method == 'POST':
        form = forms.CreateEquipmentForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data

            with connection.cursor() as cursor:
                components_ids = form_data['components'].values_list('component_id', flat=True)
                is_available = form_data.get('is_available', True)
                
                cursor.execute(
                    'CALL insert_equipment(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    [
                        form_data['type'].equipment_type_id, 
                        form_data['name'],
                        form_data['serial_number'],
                        form_data['value'],
                        is_available,
                        list(components_ids),
                        form_data['production_description'],
                        form_data['production_start'],
                        form_data['production_end'],
                        form_data['labor_type'].labor_type_id,
                    ]
                )
            return redirect(list_equipments)
    else:
        form = forms.CreateEquipmentForm()

    context = {'form': form}
    return render(request, 'app/equipments/add-equipment.html', context=context)

def edit_equipment(request, id):
    equipment = get_object_or_404(models.equipments, equipment_id=id)
    if request.method == 'POST':
        form = forms.EditEquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form_data = form.cleaned_data
            components_ids = form_data['components'].values_list('component_id', flat=True)

            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_equipment(%s, %s, %s, %s::integer[])',
                    [
                        id,
                        form_data['name'],
                        form_data['value'],
                        list(components_ids)
                    ]
                )
            return redirect(list_equipments)
    else:
        form = forms.EditEquipmentForm(instance=equipment)

    context = {'form': form, 'equipment': equipment}
    return render(request, 'app/equipments/edit-equipment.html', context=context)

def edit_production(request, id):
    equipment = get_object_or_404(models.production, equipment__equipment_id=id)
    if request.method == 'POST':
        form = forms.EditProductionForm(request.POST, instance=equipment)
        if form.is_valid():
            form_data = form.cleaned_data

            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_production(%s, %s, %s, %s, %s)',
                    [
                        id,
                        form_data['description'],
                        form_data['production_start'],
                        form_data['production_end'],
                        form_data['labor_type'].labor_type_id,
                    ]
                )
            return redirect(list_equipments)
    else:
        form = forms.EditProductionForm(instance=equipment)

    context = {'form': form, 'equipment': equipment}
    return render(request, 'app/equipments/edit-production.html', context=context)

def delete_equipment(request, id):
    equipment = get_object_or_404(models.equipments, equipment_id=id)
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_equipment(%s)', [id])
    return redirect(list_equipments)

def order_equipment(request, id):
    equipment = get_object_or_404(models.equipments, equipment_id=id)
    production = get_object_or_404(models.production, equipment_id=id)
    description = production.description

    def split_description(description):
        pairs = description.split(', ')
        result = {}
        for pair in pairs:
            name, value = pair.split(':')
            result[name.strip()] = value.strip()
        return result

    data = split_description(description)
    data['_pgsequipment_id'] = id

    user_id = request.user.id
    with connection.cursor() as cursor:
        cursor.execute('CALL order_equipment(%s, %s)', [id, user_id])

        database = mongoCon
        collection = database['Sales']
        collection.insert_one(data)

    return redirect(list_equipments)

def list_shipping_guides(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM list_shipping_guides()')
        columns = [col[0] for col in cursor.description]
        shipping_guides = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {'shipping_guides': shipping_guides}
    return render(request, 'app/guides/shipping-guides.html', context=context)

def edit_shipping_guide(request, id):
    shipping_guide = get_object_or_404(models.shipping_guide, guide_id=id)
    if request.method == 'POST':
        form = forms.ShippingGuidesForm(request.POST, instance=shipping_guide)
        if form.is_valid():
            form_data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute(
                    'CALL edit_shipping_guide(%s, %s, %s)',
                    [
                        form_data['shipping_date'],
                        form_data['delivery_date'],
                        id,
                    ]
                )
            return redirect(list_shipping_guides)
    else:
        form = forms.ShippingGuidesForm(instance=shipping_guide)

    context = {'form': form, 'shipping_guide': shipping_guide}
    return render(request, 'app/guides/edit-guide.html', context=context)


def export_to_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT export_component_info();")
        result = cursor.fetchone()
        component_info_json = result[0] if result else None

    if component_info_json:
        json_string = json.dumps(component_info_json, indent=2)
        response = HttpResponse(json_string, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=exported_data.json'

        return response
    else:
        return JsonResponse({'error': 'There is no data to be exported'})

def import_from_json(request):
    if request.method == 'POST':
        json_file = request.FILES.get('json_file')

        if json_file:
            if not json_file.content_type == 'application/json':
                return JsonResponse({'error': 'Invalid file type. Please upload a JSON file.'}, status=400)

            try:
                json_data = json.load(json_file)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT import_component_info(%s);", [json.dumps(json_data)])

                return redirect(list_components)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'})
        else:
            return JsonResponse({'error': 'No file provided'})
    else:
        return JsonResponse({'error': 'Invalid request method'})