define(['knockout',
        'knockout-mapping',
        'views/list',
        'viewmodels/function',
        'bindings/chosen'],
function (ko, koMapping, ListView, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/export-address', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var self = this;
            this.external_address_url = params.config.external_address_url;

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(_.contains(this.config.triggering_nodegroups(), card.nodegroup_id))){
                    this.config.triggering_nodegroups.push(card.nodegroup_id);
                }
            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/export-address.htm'
        }
    });
})
