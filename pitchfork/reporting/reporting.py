
from flask import render_template, redirect, url_for, \
    request, flash, g, current_app, jsonify
from bson.objectid import ObjectId
from . import bp, check_perms


import pymongo
import forms
import re
import json


import reporting_helper as help


@bp.route('/')
@check_perms(request)
def reporting():
    title = "Application Reporting"
    report_form = help.generate_reporting_form()
    return render_template(
        'reporting_index.html',
        title=title,
        form=report_form
    )


@bp.route('/setup', methods=['GET', 'POST'])
@check_perms(request)
def reporting_manage():
    error = True
    title = "Setup Application Reporting"
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    report_fields = g.db.reporting.find()

    if report_settings:
        form = forms.ReportGlobal(
            collection=report_settings.get('collection'),
            description=report_settings.get('description'),
            enabled=report_settings.get('enabled')
        )
    else:
        form = forms.ReportGlobal()

    if request.method == 'POST' and form.validate_on_submit():
        enabled = False
        if request.form.get('enabled'):
            enabled = True

        collection = request.form.get('collection').lower()
        g.db.settings.update(
            {
                '_id': settings.get('_id')
            },
            {
                '$set': {
                    'reporting': {
                        'collection': collection,
                        'enabled': enabled,
                        'description': request.form.get('description')
                    }
                }
            }
        )

        return redirect(url_for('reporting.reporting_manage'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form validation error. Please'
            ' check the form and resend request'
        )
        return render_template(
            'reporting.html',
            title=title,
            form=form,
            report_settings=report_settings,
            report_fields=report_fields,
            error=error
        )

    else:
        return render_template(
            'reporting.html',
            title=title,
            form=form,
            report_settings=report_settings,
            report_fields=report_fields
        )


@bp.route('/fields/manage')
@check_perms(request)
def reporting_fields_manage(field_id=None):
    title = "Current Fields"
    manage = True
    settings = g.db.settings.find_one()
    report_fields = g.db.reporting.find()
    return render_template(
        'reporting.html',
        title=title,
        report_fields=report_fields,
        manage=manage
    )


@bp.route('/fields/edit/<field_id>', methods=['GET', 'POST'])
@bp.route('/fields/add', methods=['GET', 'POST'])
@check_perms(request)
def reporting_fields_add_edit(field_id=None):
    error = True
    title = "Setup Reporting Fields"
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    report_fields = g.db.reporting.find()

    if field_id:
        edit_field = g.db.reporting.find_one({'_id': ObjectId(field_id)})
        form = forms.ReportFields(
            field_name=edit_field.get('field_name'),
            data_type=edit_field.get('data_type'),
            searchable=edit_field.get('searchable'),
            description=edit_field.get('description'),
            field_display=edit_field.get('field_display'),
            field_display_data=edit_field.get('field_display_data')
        )
    else:
        form = forms.ReportFields()

    if request.method == 'POST' and form.validate_on_submit():
        searchable = False
        if request.form.get('searchable'):
            searchable = True

        collection = report_settings.get('collection')
        test_data = getattr(g.db, collection).find_one()

        if field_id:
            g.db.reporting.update(
                {
                    '_id': edit_field.get('_id')
                },
                {
                    '$set': {
                        'searchable': searchable,
                        'description': request.form.get('description'),
                        'data_type': request.form.get('data_type'),
                        'field_name': request.form.get('field_name').lower(),
                        'field_display': request.form.get('field_display'),
                        'field_display_data': request.form.get(
                            'field_display_data'
                        )
                    }
                }
            )
        else:
            if not test_data:
                flash(
                    'Collection has no data in it.'
                    ' Please insert data and resubmit form'
                )
                return render_template(
                    'reporting.html',
                    title=title,
                    form=form,
                    report_fields=report_fields,
                    error=error
                )

            found = False
            found = help.check_for_field(
                test_data,
                request.form.get('field_name').lower(),
                found
            )

            if found:
                g.db.reporting.insert(
                    {
                        'searchable': searchable,
                        'description': request.form.get('description'),
                        'data_type': request.form.get('data_type'),
                        'field_name': request.form.get('field_name').lower(),
                        'field_display': request.form.get('field_display'),
                        'field_display_data': request.form.get(
                            'field_display_data'
                        )
                    }
                )
            else:
                flash(
                    'Field name could not be found in collection'
                    ' Please check the name and resubmit form'
                )
                return render_template(
                    'reporting.html',
                    title=title,
                    form=form,
                    report_fields=report_fields,
                    error=error
                )

        return redirect(url_for('reporting.reporting_fields_manage'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form validation error. Please'
            ' check the form and resend request'
        )
        return render_template(
            'reporting.html',
            title=title,
            form=form,
            report_fields=report_fields,
            error=error
        )

    else:
        return render_template(
            'reporting.html',
            title=title,
            form=form,
            report_fields=report_fields
        )


@bp.route('/fields/remove/<field_id>')
@check_perms(request)
def reporting_field_remove(field_id):
    if field_id:
        field_to_remove = g.db.reporting.find_one(
            {
                '_id': ObjectId(field_id)
            }
        )
        if field_to_remove:
            g.db.reporting.remove({'_id': field_to_remove.get('_id')})
            message = "Field has been removed."
        else:
            message = "Field could not be found, and nothing was removed."
    else:
        message = "You must specify a field to remove."

    flash(message)
    return redirect(url_for('reporting.reporting_fields_manage'))


@bp.route('/fields/action/<field_id>/<take_action>')
@check_perms(request)
def reporting_field_action(field_id, take_action):
    if field_id:
        field_to_take_action = g.db.reporting.find_one(
            {
                '_id': ObjectId(field_id)
            }
        )
        if field_to_take_action:
            if take_action == 'activate':
                g.db.reporting.update(
                    {
                        '_id': field_to_take_action.get('_id')
                    }, {
                        '$set': {
                            'searchable': True
                        }
                    }
                )
                message = "Field was marked as active"
            elif take_action == 'deactivate':
                g.db.reporting.update(
                    {
                        '_id': field_to_take_action.get('_id')
                    }, {
                        '$set': {
                            'searchable': False
                        }
                    }
                )
                message = "Field was marked as inactive"
            else:
                message = "Incorrect action specified. No action taken"
        else:
            message = "Field could not be found. No action was taken"
    else:
        message = "You must specify a field to take action on."

    flash(message)
    return redirect(url_for('reporting.reporting_fields_manage'))


@bp.route('/generate', methods=['POST'])
@check_perms(request)
def generate_report():
    results = []
    title = "Query Results"
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    if report_settings.get('enabled'):
        query = help.generate_reporting_query(request)
        collection = report_settings.get('collection')
        results = getattr(g.db, collection).find(query).sort(
            'completed_at', pymongo.DESCENDING
        )
    return render_template(
        '_report_results.html',
        title=title,
        results=results
    )


@bp.route('/generate/details/<history_id>')
@check_perms(request)
def generate_details_report(history_id):
    item = g.db.history.find_one({'_id': ObjectId(history_id)})
    if item:
        return render_template(
            '_detail_call_history.html',
            item=item
        )
