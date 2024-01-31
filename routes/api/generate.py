import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, send_file
from services.generate import GenerateService
from utils.storybook_generate import BuildBook
from utils.pdf_generate import build_pdf

load_dotenv()

generate = Blueprint("generate", __name__)


@generate.route("/generate/chart", methods=["POST"])
def generate_chart():
    try:
        query = request.form.get("query")
        content = request.form.get("content")
        result = GenerateService.generateChart(query, content)
        return jsonify({"status": True, "result": result})
    except Exception as e:
        print(e)
        return jsonify({"status": False, "message": "Error: " + str(e)})


@generate.route("/generate/smart_extraction/chart", methods=["POST"])
def generate_analysis():
    try:
        requestData = request.get_json()
        query = requestData["query"]
        viewsName = requestData["views_name"]
        tenant = requestData["tenant"]
        dataSchema = requestData["data_schema"]
        schema = requestData["schema"]
        print(query, viewsName, tenant, dataSchema, schema)
        result, sql, flag = GenerateService.generateChartFromDBData(
            viewsName, tenant, query, dataSchema, schema
        )

        if flag == 1:
            return jsonify({"status": True, "result": result, "sql": sql})
        else:
            return jsonify({"status": False, "result": result, "sql": sql})
    except Exception as e:
        return jsonify({"status": False, "message": "Error: " + str(e)})


@generate.route("/generate/smart_extraction/statistics", methods=["POST"])
def generate_statistics():
    try:
        requestData = request.get_json()
        query = requestData["query"]
        viewsName = requestData["views_name"]
        tenant = requestData["tenant"]
        dataSchema = requestData["data_schema"]
        schema = requestData["schema"]
        print(query, viewsName, tenant, dataSchema, schema)
        result, sql, flag = GenerateService.generateStatisticsFromDBData(
            viewsName, tenant, query, dataSchema, schema
        )

        if flag == 1:
            return jsonify({"status": True, "result": result, "sql": sql})
        else:
            return jsonify({"status": False, "result": result, "sql": sql})
    except Exception as e:
        return jsonify({"status": False, "message": "Error: " + str(e)})

@generate.route("/generate/storybook", methods=["POST"])
def generate_storybook():
    try:
        requestData = request.get_json()
        query = requestData["query"]
        style = requestData["style"]
        print(query, style)
        build_book = BuildBook(os.getenv("OPENAI_GPT4_MODEL_NAME"), query, style)
        pages = build_book.list_of_tuples
        finished_pdf = build_pdf(pages, 'result.pdf')
        file_bytes = open(finished_pdf, 'rb').read()
        
        # return file_bytes
        return send_file(finished_pdf, as_attachment=True, download_name="storybook.pdf")
    except Exception as e:
        return jsonify({"status": False, "message": "Error: " + str(e)})