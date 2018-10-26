var Wall = {
    createNew: function(name, barnLength, barnWidth) {
        var wall = {};
        wall.name = name;
        wall.length = 0;
        wall.width = 0;
        wall.waterHeight = 0;
        wall.height = 0;
        wall.thickness = 0;
        wall.groupNum = 0;
        wall.barnLength = barnLength;
        wall.barnWidth =barnWidth;
        wall.area = 0;
        wall.waterDelta=0;
        wall.girth = 0;
    return wall;
    }
}

var getWalls = function() {
    var wallList = [Wall.createNew("女儿墙", 0, 0), Wall.createNew("机房墙", 1,1), Wall.createNew("管井墙",1,1), 
        Wall.createNew("设备基础",1,1), Wall.createNew("管根",1,1)];
        /*
    for (let i = 1; i < 5; i++) {
        wallList[i]['barnLength'] = 1;
        wallList[i]['barnWidth'] = 1;
    }
    */
    return wallList;
}


var Material = {
    createNew: function(name, absorbRate, permeateRate) {
        var material = {};
        material.name = name;
        material.absorbRate = absorbRate;
        material.permeateRate = permeateRate;
        return material;
    }
}

var getMeterials = function() {
    var materials = []
    m = ["混凝土", "C30以上高标号混凝土", "添加抗渗剂混凝土", "二次浇捣混凝土", "二次浇捣高标混凝土", "二次浇捣抗渗混凝土", "水泥砂浆",
        "添加抗渗剂水泥砂浆", "粘土砖墙", "加气块墙", "憎水型保温", "吸水型保温", "防水层", "隔汽层"];
    absorbRates = [0.1, 0.08, 0.07, 0.1, 0.08, 0.07, 0.21, 0.15, 0.31, 0.56, 0.04, 0.7, 0, 0]
    permeateRates = [0.1, 0.08, 0.07, 0.2, 0.16, 0.14, 0.1, 0.07, 1, 1, 0.1, 0.1, 0.1, 0.2]
    for (let i = 0; i < 14; i++) {
        materials[i] = Material.createNew(m[i], absorbRates[i], permeateRates[i])
    }
    return materials
}

var RoomSpace = {
    createNew: function(name, materialOptions) {
        var room = {};
        room.name = name;
        room.materialOptions = materialOptions;
        room.material = 0;
        room.thickness = 0;
        room.area = 0;
        room.permeateSum = 0;
        room.waterSum = 0;
        return room;
    }
}

var getRooms = function() {
    var rooms = []
    name = ["屋面结构层", "屋面保温层", "屋面防水层", "屋面隔气层", "屋面找平层", "屋面保护层", 
        "女儿墙", "机房墙", "管井墙", "设备基础", "管根"];
    materialOptions = [[0,1,2],[10,11],[12],[13],[6,7],[3,4,5,6,7],9,9,8,5,7];
    for (let i = 0; i < 11; i++) {
        rooms[i] = RoomSpace.createNew(name[i], materialOptions[i]);
    }
    return rooms
}

var getRains = function() {
    var rains = [['北京', '20', '0', '244.2', '7/31', '7月下旬'], ['海口', '110', '13', '331.2', '10/5', '10月上旬'], ['广州', '77', '3', '284.9', '6/6', '6月上旬'], ['武汉', '56', '9', '317.4', '6/9', '6月上旬'], ['南昌', '56', '7', '289', '6/24', '6月下旬'], ['南宁', '40', '3', '229.9', '7/3', '7月上旬'], ['福州', '37', '1', '195.6', '10/3', '10月上旬'], ['南京', '36', '1', '207.2', '7/5', '7月上旬'], ['成都', '26', '3', '201.3', '7/13', '7月中旬'], ['济南', '25', '3', '246.4', '10/7', '10月上旬'], ['杭州', '25', '1', '298.4', '7/13', '8月中旬'], ['重庆', '24', '2', '271', '7/17', '7月中旬'], ['长沙', '24', '1', '249.5', '6/7', '6月上旬'], ['上海', '23', '2', '204.4', '8/5', '8月上旬'], ['合肥', '19', '1', '238.4', '6/13', '6月中旬'], ['沈阳', '18', '1', '215.5', '8/21', '8月下旬'], ['贵阳', '17', '1', '197.3', '7/2', '7月上旬'], ['郑州', '16', '0', '189.4', '7/2', '7月上旬'], ['天津', '14', '1', '158.1', '7/25', '7月下旬'], ['石家庄', '13', '1', '359.3', '8/4', '8月上旬'], ['长春', '9', '1', '130.4', '7/31', '7月下旬'], ['呼和浩特', '7', '0', '210.1', '7/27', '7月下旬'], ['昆明', '6', '0', '165.4', '6/7', '6月上旬'], ['哈尔滨', '3', '1', '155.3', '7/24', '7月下旬'], ['西安', '2', '0', '117.3', '8/9', '8月上旬'], ['银川', '1', '1', '113.3', '7/30', '7月下旬'], ['太原', '1', '0', '183.5', '7/27', '7月下旬'], ['兰州', '0', '0', '96.8', '8/7', '8月上旬'], ['西宁', '0', '0', '62.2', '8/19', '8月中旬'], ['乌鲁木齐', '0', '0', '57.7', '6/11', '6月中旬'], ['拉萨', '0', '0', '41.6', '7/28', '7月下旬']]
    return rains
}








//var rooms = getRooms()
//console.log(rooms)
