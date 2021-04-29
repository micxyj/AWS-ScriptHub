import os
import json
import logging


# logger = logging.getLogger(__name__)


def input_handler(data, context):
    """ Pre-process request input before it is sent to TensorFlow Serving REST API
    Args:
        data (obj): the request data, in format of dict or string
        context (Context): an object containing request and configuration details
    Returns:
        (dict): a JSON-serializable dict that contains request body and headers
    """
    # logger.info(data)
    
    if context.request_content_type == 'application/json':
        # pass through json (assumes it's correctly formed)
        d = data.read().decode('utf-8')
        
        # transfer list to classify examples
        d_lst = json.loads(d)
        examples = [{'0': i[0], '1': i[1], '2': i[2], '3': i[3]} for i in d_lst]
        
        # jsonify data to model serving
        return json.dumps({'examples': examples})

    raise ValueError('{{"error": "unsupported content type {}"}}'.format(
        context.request_content_type or "unknown"))


def output_handler(data, context):
    """Post-process TensorFlow Serving output before it is returned to the client.
    Args:
        data (obj): the TensorFlow serving response
        context (Context): an object containing request and configuration details
    Returns:
        (bytes, string): data to return to client, response content type
    """
    if data.status_code != 200:
        raise ValueError(data.content.decode('utf-8'))

    response_content_type = context.accept_header
    prediction = data.content
    return prediction, response_content_type
