from django import template

class InvalidParamsError(template.TemplateSyntaxError):
    ''' Custom exception class to distinguish usual TemplateSyntaxErrors 
        and validation errors for templatetags introduced by ``validate_params``
        function'''
    pass

def validate_params(bits, arguments_count, keyword_positions):
    '''
        Raises exception if passed params (`bits`) do not match signature.
        Signature is defined by `arguments_count` (acceptible number of params) and
        keyword_positions (dictionary with positions in keys and keywords in values,
        for ex. {2:'by', 4:'of', 5:'type', 7:'as'}).            
    '''    
    
    if len(bits) != arguments_count+1:
        raise InvalidParamsError("'%s' tag takes %d arguments" % (bits[0], arguments_count,))
    
    for pos in keyword_positions:
        value = keyword_positions[pos]
        if bits[pos] != value:
            raise InvalidParamsError("argument #%d to '%s' tag must be '%s'" % (pos, bits[0], value))
