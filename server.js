const _ = require('lodash');
const cors = require('cors');
const csv = require('csv-parser');
const express = require('express');
const fs = require('fs');

const app = express();
app.use(cors());

const port = 3000;

var paths = [];
var routes = [];

app.get('/', (req, res) => {
  res.send('Hello World!')
});

app.get('/routes', (req, res) => {
  const start = req.query.start;
  const end = req.query.end;

  const pathsSlice = paths.slice(start, end);
  const routesSlice = _.map(pathsSlice, path => {
    return _.find(routes, route => {
      return (
        path['startCentroidLatitude'] == route['originLat'] &&
        path['startCentroidLongitude'] == route['originLng'] &&
        path['endCentroidLatitude'] == route['destLat'] &&
        path['endCentroidLongitude'] == route['destLng']
      )
    })
  })

  const pathsAndRoutes = _.zip(pathsSlice, routesSlice)

  const results = _.map(pathsAndRoutes, pathAndRoute => {
    const [path, route] = pathAndRoute;

    return {
      ...path,
      encodedPoints: route['encodedPoints']
    }
  })

  res.send({
    data: results,
    total: paths.length
  });
});

app.listen(port, () => {
  // Read the scooter paths
  fs.createReadStream('scooter_paths.csv')
    .pipe(csv())
    .on('data', (data) => paths.push(data))
    .on('end', () => {
      paths = _.map(paths, path => {
        return _.mapKeys(path, (value, key) => {
          return _.camelCase(key)
        });
      });

      // Read the routes for those paths
      fs.createReadStream('routes.csv')
        .pipe(csv())
        .on('data', (data) => routes.push(data))
        .on('end', () => {
          routes = _.map(routes, route => {
            return _.mapKeys(route, (value, key) => {
              return _.camelCase(key)
            });
          });

          console.log(`Started service on localhost:${port}`);
        });
    });
});
