
from . import bp
from pitchfork.adminbp.decorators import check_perms
from flask import render_template, redirect, url_for, request, flash, g
from flask import jsonify, make_response
from bson.objectid import ObjectId
from bson.son import SON


import pymongo
import forms
import helper as help


SORT_FIELD = 'completed_at'
TREND_FIELD = '$completed_at'


@bp.route('/')
@check_perms(request)
def reporting():
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    report_form = help.generate_reporting_form(report_settings)
    return render_template(
        'engine/reporting_index.html',
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
            enabled=report_settings.get('enabled'),
            allow_team=report_settings.get('allow_team')
        )
    else:
        form = forms.ReportGlobal()

    if request.method == 'POST' and form.validate_on_submit():
        enabled = bool(request.form.get('enabled'))
        allow_team = bool(request.form.get('allow_team'))
        collection = request.form.get('collection').lower()
        g.db.settings.update(
            {
                '_id': settings.get('_id')
            }, {
                '$set': {
                    'reporting': {
                        'collection': collection,
                        'enabled': enabled,
                        'allow_team': allow_team,
                        'description': request.form.get('description')
                    }
                }
            }
        )
        flash('Reporting settings successfully updated')
        return redirect(url_for('engine.reporting_manage'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form validation error. Please'
            ' check the form and resend request',
            'error'
        )
        return render_template(
            'engine/engine.html',
            title=title,
            form=form,
            report_settings=report_settings,
            report_fields=report_fields,
            error=error
        )

    else:
        return render_template(
            'engine/engine.html',
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
    report_fields = g.db.reporting.find()
    return render_template(
        'engine/engine.html',
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
            field_display_data=edit_field.get('field_display_data'),
            field_display_label=edit_field.get('field_display_label'),
            graphable=edit_field.get('graphable')
        )
    else:
        form = forms.ReportFields()

    if request.method == 'POST' and form.validate_on_submit():
        collection = report_settings.get('collection')
        test_data = getattr(g.db, collection).find_one()
        field_name = request.form.get('field_name').strip().lower()
        if field_id:
            g.db.reporting.update(
                {
                    '_id': edit_field.get('_id')
                }, {
                    '$set': {
                        'searchable': bool(request.form.get('searchable')),
                        'description': request.form.get('description'),
                        'data_type': request.form.get('data_type'),
                        'field_name': field_name,
                        'field_display': request.form.get('field_display'),
                        'field_display_data': request.form.get(
                            'field_display_data'
                        ),
                        'field_display_label': request.form.get(
                            'field_display_label'
                        ),
                        'graphable': bool(request.form.get('graphable'))
                    }
                }
            )
            flash('Field was successfully updated')
        else:
            if not test_data:
                flash(
                    'Collection has no data in it.'
                    ' Please insert data and resubmit form',
                    'error'
                )
                return render_template(
                    'engine/engine.html',
                    title=title,
                    form=form,
                    report_fields=report_fields,
                    error=error
                )

            found = help.check_for_field(field_name, collection)
            if found:
                g.db.reporting.insert(
                    {
                        'searchable': bool(request.form.get('searchable')),
                        'description': request.form.get('description'),
                        'data_type': request.form.get('data_type'),
                        'field_name': field_name,
                        'field_display': request.form.get('field_display'),
                        'field_display_data': request.form.get(
                            'field_display_data'
                        ),
                        'field_display_label': request.form.get(
                            'field_display_label'
                        ),
                        'graphable': bool(request.form.get('graphable'))
                    }
                )
                flash('Field was successfully added')
            else:
                flash(
                    'Field name could not be found in collection.'
                    ' Please check the name and resubmit form',
                    'error'
                )
                return render_template(
                    'engine/engine.html',
                    title=title,
                    form=form,
                    report_fields=report_fields,
                    error=error
                )

        return redirect(url_for('engine.reporting_fields_manage'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash(
            'Form validation error. Please'
            ' check the form and resend request',
            'error'
        )
        return render_template(
            'engine/engine.html',
            title=title,
            form=form,
            report_fields=report_fields,
            error=error
        )

    else:
        return render_template(
            'engine/engine.html',
            title=title,
            form=form,
            report_fields=report_fields
        )


@bp.route('/fields/remove/<field_id>')
@check_perms(request)
def reporting_field_remove(field_id):
    field_to_remove = g.db.reporting.find_one({'_id': ObjectId(field_id)})
    if field_to_remove:
        g.db.reporting.remove({'_id': field_to_remove.get('_id')})
        flash('Field has been removed')
    else:
        flash('Field could not be found, and nothing was removed', 'error')

    return redirect(url_for('engine.reporting_fields_manage'))


@bp.route('/fields/action/<field_id>/<take_action>')
@check_perms(request)
def reporting_field_action(field_id, take_action):
    field_to_take_action = g.db.reporting.find_one({'_id': ObjectId(field_id)})
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
            flash('Field was marked as active')
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
            flash('Field was marked as inactive')
        else:
            flash('Incorrect action specified. No action taken', 'error')
    else:
        flash('Field could not be found. No action was taken', 'error')

    return redirect(url_for('engine.reporting_fields_manage'))


@bp.route('/view/<item_id>')
@check_perms(request)
def view_item_details(item_id):
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    collection = report_settings.get('collection')
    item = getattr(g.db, collection).find_one({'_id': ObjectId(item_id)})
    if item:
        return render_template(
            'engine/_item_display.html',
            item=item
        )
    else:
        flash('Item could not be found to display', 'error')
        return redirect(url_for('index'))


@bp.route('/generate', methods=['POST'])
@check_perms(request)
def generate_report():
    results = []
    title = "Query Results"
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    if report_settings.get('enabled'):
        if request.json:
            query = help.generate_reporting_query(request)
        else:
            query = {}

        collection = report_settings.get('collection')
        results = getattr(g.db, collection).find(query).sort(
            SORT_FIELD, pymongo.DESCENDING
        )
        graph_data, graph_keys, graph_labels = help.generate_graph_data(
            results
        )
    return render_template(
        'engine/_report_results.html',
        title=title,
        results=results.rewind(),
        graph_data=graph_data,
        graph_keys=graph_keys,
        graph_labels=graph_labels
    )


@bp.route('/generate/csv', methods=['POST'])
@check_perms(request)
def generate_csv_report():
    results = []
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    if report_settings.get('enabled'):
        if request.form:
            query = help.generate_reporting_query(request)
        else:
            query = {}

        collection = report_settings.get('collection')
        results = getattr(g.db, collection).find(query).sort(
            SORT_FIELD, pymongo.DESCENDING
        )

    template = render_template(
        'engine/generated_report.csv',
        results=results
    )
    response = make_response(template)
    response.headers['Content-Type'] = 'application/csv'
    response.headers['Content-Disposition'] = (
        'attachment; filename="generated_report.csv"'
    )
    return response


@bp.route('/generate/trend', methods=['POST'])
@check_perms(request)
def generate_trend_data():
    settings = g.db.settings.find_one()
    report_settings = settings.get('reporting')
    collection = report_settings.get('collection')
    delta = help.get_delta_days_for_trending(request, collection)
    title = '%s : Trending Report' % request.json.get('search_on')
    if report_settings.get('enabled'):
        query = help.generate_reporting_trend_query(request)
        match = {
            '$match': query
        }
        project = {
            '$project': {
                '_id': 0,
                'month': {
                    '$month': TREND_FIELD
                },
                'year': {
                    '$year': TREND_FIELD
                },
                'day': {
                    '$dayOfMonth': TREND_FIELD
                }
            }
        }
        group = {
            '$group': {
                '_id': {
                    'year': '$year',
                    'month': '$month',
                    'day': '$day'
                },
                'count': {
                    '$sum': 1
                }
            }
        }
        sort = {
            '$sort': SON(
                [
                    ('_id', 1)
                ]
            )
        }
        results_query = [
            match,
            project,
            group,
            sort
        ]
        results = getattr(g.db, collection).aggregate(results_query)
        if delta < 21:
            graph_data, graph_labels = help.generate_graph_trending_data(
                results,
                request
            )
            return jsonify(
                points=graph_data,
                labels=graph_labels,
                delta=delta,
                title=title
            )
        elif delta < 63:
            week_label, week_counts = help.generate_weekly_trend(
                results,
                request
            )
            return jsonify(
                points=week_counts,
                labels=week_label,
                delta=delta,
                title=title
            )
        else:
            project = {
                '$project': {
                    '_id': 0,
                    'month': {
                        '$month': TREND_FIELD
                    },
                    'year': {
                        '$year': TREND_FIELD
                    }
                }
            }
            group = {
                '$group': {
                    '_id': {
                        'month': '$month',
                        'year': '$year'
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            }
            month_query = [
                match,
                project,
                group,
                sort
            ]
            results = getattr(g.db, collection).aggregate(month_query)
            month_label, month_counts = help.generate_monthly_trend(
                results,
                request
            )
            return jsonify(
                points=month_counts,
                labels=month_label,
                delta=delta,
                title=title
            )
