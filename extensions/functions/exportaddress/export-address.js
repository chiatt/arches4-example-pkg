define(['jquery',
        'underscore',
        'knockout',
        'knockout-mapping',
        'views/list',
        'viewmodels/function',
        'bindings/chosen'],
function ($, _, ko, koMapping, ListView, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/export-address', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var self = this;
            this.external_address_url = params.config.external_address_url;
            this.externalReference = params.config.external_reference_node;
            this.geometry = params.config.geometry_node;
            this.targetFields = params.config.target_fields;
            this.targetFieldNames = _.map(this.targetFields(), function(field){
                return field.name()
            });
            this.defaultNode = ko.observable(this.graph.nodes[0])
            this.nodes = ko.observableArray();
            this.graph.nodes.forEach(function(node){
                this.nodes.push(node);
            }, this);

            this.external_address_url.subscribe(function(val){                
                if (val != '') {
                    $.ajax({
                        url: val + '/?f=pjson'
                    }).done(function(data) {
                        _.each(JSON.parse(data).fields, function(field){
                            if (field.editable && _.contains(this.targetFieldNames, field.name) === false) {
                                fieldProperties = {'name': field.name, 'type': field.actualType, 'node': ko.observable('')}
                                this.targetFields.push(fieldProperties);
                                fieldProperties.node.subscribe(function(val){
                                    console.log(console.log('update triggering nodegroups here'))
                                });
                            }
                        }, self)

                    }).fail(function(err) {
                        console.log(err)
                    });
                }
            }, self)

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(_.contains(this.config.triggering_nodegroups(), card.nodegroup_id))){
                    this.config.triggering_nodegroups.push(card.nodegroup_id);
                }
            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 1000);
        },
        template: {
            require: 'text!templates/views/components/functions/export-address.htm'
        }
    });
})
